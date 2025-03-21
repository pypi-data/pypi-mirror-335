import ast
import os
from binascii import crc32
from collections import defaultdict
from typing import List, Optional, Union
from uuid import UUID

from .client import AsyncHandlerReturnType, Client
from .logging import internal_logger
from .schemas.events import (
    ArgumentType,
    CodeBlockType,
    FileDeclaration,
    FunctionArgument,
    FunctionDeclaration,
    ScopeNode,
)
from .schemas.responses import FileDeclarations as FileDeclarationsResponse


def parse_function_node_arguments(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
) -> List[FunctionArgument]:
    # We use this specific order to match the order of the arguments in the function signature.
    # paramters look like: (positional_only, /, positional_or_keyword, *varargs, keyword_only, **kwargs),
    # while all of them are optional and can be omitted
    arguments = []
    if hasattr(node.args, "posonlyargs"):  # Added in Python 3.8
        for arg in node.args.posonlyargs:
            arguments.append(FunctionArgument(arg.arg, ArgumentType.POSITIONAL_ONLY))
    for arg in node.args.args:
        arguments.append(FunctionArgument(arg.arg, ArgumentType.ARG))
    if node.args.vararg:
        arguments.append(FunctionArgument(node.args.vararg.arg, ArgumentType.VARARG))
    for arg in node.args.kwonlyargs:
        arguments.append(FunctionArgument(arg.arg, ArgumentType.KEYWORD_ONLY))
    if node.args.kwarg:
        arguments.append(FunctionArgument(node.args.kwarg.arg, ArgumentType.KWARG))
    return arguments


class Declaration:
    __match_args__ = (
        "function_id",
        "name",
        "path",
        "start_line",
        "end_line",
        "is_async",
        "source_code_hash",
        "code_block_type",
        "file_checksum",
    )

    def __init__(
        self,
        function_id: UUID,
        name: str,
        path: str,
        start_line: int,
        end_line: Optional[int],
        is_async: bool,
        source_code_hash: str,
        code_block_type: CodeBlockType,
        file_checksum: int,
        arguments: Optional[List[FunctionArgument]] = None,
        scope: Optional[List[ScopeNode]] = None,
    ):
        self.function_id = function_id
        self.name = name
        self.path = os.path.normpath(path)
        self.start_line = start_line
        self.end_line = end_line
        self.is_async = is_async
        self.source_code_hash = source_code_hash
        self.code_block_type = code_block_type
        self.file_checksum = file_checksum
        self.arguments = arguments or []
        self.scope = scope[:] if scope else []
        self.declarations_count = 0

    @staticmethod
    def get_lineno(
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef],
    ) -> int:
        if node.decorator_list:
            return node.decorator_list[0].lineno
        return node.lineno

    @classmethod
    def from_function_node(
        cls,
        function_id: UUID,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        source_code_hash: str,
        path: str,
        is_async: bool,
        scope: List[ScopeNode],
        file_checksum: int,
    ) -> "Declaration":
        return cls(
            function_id,
            node.name,
            path,
            cls.get_lineno(node),
            getattr(node, "end_lineno", None),
            is_async,
            source_code_hash,
            CodeBlockType.FUNCTION,
            file_checksum,
            parse_function_node_arguments(node),
            scope,
        )

    @classmethod
    def from_class_node(
        cls,
        class_id: UUID,
        node: ast.ClassDef,
        source_code_hash: str,
        path: str,
        file_checksum: int,
        scope: List[ScopeNode],
    ) -> "Declaration":
        return cls(
            class_id,
            node.name,
            path,
            cls.get_lineno(node),
            getattr(node, "end_lineno", None),
            False,
            source_code_hash,
            CodeBlockType.CLASS,
            file_checksum,
            None,
            scope,
        )

    @classmethod
    def from_module_node(
        cls,
        module_id: UUID,
        node: ast.Module,
        source_code_hash: str,
        path: str,
        file_checksum: int,
    ) -> "Declaration":
        return cls(
            module_id,
            "<module>",
            path,
            1,
            getattr(node, "end_lineno", None),
            False,
            source_code_hash,
            CodeBlockType.MODULE,
            file_checksum,
            None,
            [],
        )

    def set_declarations_count(self, count: int) -> None:
        self.declarations_count = count

    def for_request(self) -> "FunctionDeclaration":
        return FunctionDeclaration(
            self.path,
            str(self.function_id),
            self.is_async,
            self.name,
            self.source_code_hash,
            self.start_line,
            self.end_line,
            self.code_block_type,
            self.file_checksum,
            self.declarations_count,
            self.arguments,
            self.scope,
        )


class DeclarationsAggregator:
    def __init__(self) -> None:
        self.declarations = []  # type: List[Declaration]

    def add_declaration(self, declaration: Declaration) -> None:
        self.declarations.append(declaration)

    def get_and_clear_declarations(self) -> List[FunctionDeclaration]:
        declarations = [declaration.for_request() for declaration in self.declarations]
        self.clear()
        return declarations

    def clear(self) -> None:
        self.declarations = []


async def send_function_declarations(
    client: Client[AsyncHandlerReturnType], declarations: List[FunctionDeclaration]
) -> None:
    declaration_mapping = defaultdict(list)
    for func_decl in declarations:
        file_path_checksum = crc32(func_decl.file.encode())
        file_checksum = func_decl.file_checksum
        file_decl = FileDeclaration(file_path_checksum, file_checksum)
        declaration_mapping[file_decl].append(func_decl)

    unique_file_declarations: List[FileDeclaration] = sorted(
        declaration_mapping.keys(),
        key=lambda fd: f"{fd.file_path_checksum}|{fd.file_checksum}",
    )

    try:
        file_declarations_response: FileDeclarationsResponse = (
            await client.send_file_declarations(unique_file_declarations)
        )
    except Exception:
        internal_logger.exception("Failed to send file declarations")
        await client.send_batch_json(declarations, "FunctionDeclaration")
        return

    if file_declarations_response.send_all:
        await client.send_batch_json(declarations, "FunctionDeclaration")
        return

    wanted_set = set(file_declarations_response.files)
    declarations_to_send = []
    for file_decl in wanted_set:
        declarations_to_send.extend(declaration_mapping[file_decl])

    if declarations_to_send:
        await client.send_batch_json(declarations_to_send, "FunctionDeclaration")
