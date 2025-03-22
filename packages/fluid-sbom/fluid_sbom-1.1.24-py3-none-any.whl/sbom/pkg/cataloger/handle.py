from collections.abc import Callable

import reactivex
from reactivex import (
    Observable,
)
from reactivex import (
    operators as ops,
)
from reactivex.scheduler import (
    ThreadPoolScheduler,
)

from sbom.pkg.cataloger.cpp.cataloger import (
    on_next_cpp,
)
from sbom.pkg.cataloger.dart.cataloger import (
    on_next_dart,
)
from sbom.pkg.cataloger.dotnet.cataloger import (
    on_next_dotnet,
)
from sbom.pkg.cataloger.elixir.cataloger import (
    on_next_elixir,
)
from sbom.pkg.cataloger.generic.cataloger import (
    Request,
    on_next_db_file,
)
from sbom.pkg.cataloger.golang.cataloger import (
    on_next_golang,
)
from sbom.pkg.cataloger.java.cataloger import (
    on_next_java,
)
from sbom.pkg.cataloger.javascript.cataloger import (
    on_next_javascript,
)
from sbom.pkg.cataloger.php.cataloger import (
    on_next_php,
)
from sbom.pkg.cataloger.python.cataloger import (
    on_next_python,
)
from sbom.pkg.cataloger.redhat.cataloger import (
    on_next_redhat,
)
from sbom.pkg.cataloger.ruby.cataloger import (
    on_next_ruby,
)
from sbom.pkg.cataloger.rust.cataloger import (
    on_next_rust,
)
from sbom.pkg.cataloger.swift.cataloger import (
    on_next_swift,
)


def handle_parser(
    scheduler: ThreadPoolScheduler,
) -> Callable[[Observable[str]], Observable[Request]]:
    def _apply_parsers(source: Observable[str]) -> Observable[Request]:
        return source.pipe(
            ops.flat_map(
                lambda item: reactivex.merge(  # type: ignore
                    (on_next_python(reactivex.just(item, scheduler))),
                    (on_next_db_file(reactivex.just(item, scheduler))),
                    (on_next_java(reactivex.just(item, scheduler))),
                    (on_next_javascript(reactivex.just(item, scheduler))),
                    (on_next_redhat(reactivex.just(item, scheduler))),
                    (on_next_dotnet(reactivex.just(item, scheduler))),
                    (on_next_rust(reactivex.just(item, scheduler))),
                    (on_next_ruby(reactivex.just(item, scheduler))),
                    (on_next_elixir(reactivex.just(item, scheduler))),
                    (on_next_php(reactivex.just(item, scheduler))),
                    (on_next_swift(reactivex.just(item, scheduler))),
                    (on_next_dart(reactivex.just(item, scheduler))),
                    (on_next_cpp(reactivex.just(item, scheduler))),
                    (on_next_golang(reactivex.just(item, scheduler))),
                ),
            ),
        )

    return _apply_parsers
