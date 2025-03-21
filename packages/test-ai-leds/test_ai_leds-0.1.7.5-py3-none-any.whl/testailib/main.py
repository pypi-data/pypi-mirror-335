import argparse
from .handler import handle_gherkin, handle_cypress, handle_xunit, handle_unit

arguments = (
    ("generate", dict(type=str, help="O que você deseja gerar (gherkin, xunit ou cypress)")),
    ("--user-case", dict(type=str, help="Casos de usuário para gerar o Gherkin")),
    ("--vue-path", dict(type=str, help="Caminho para o arquivo vue que será usado para gerar o teste black box")),
    ("--feature-path", dict(type=str, help="O caminho para a feature para gerar o código xUnit")),
    ("--output-path", dict(type=str, help="O caminho onde o resultado da geração será salvo")),
    ("--absolute-path", dict(type=str, help="Caminho para arquivo a ser gerado o teste unitario"))
)

def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Processa os parâmetros")
    for arg in arguments:
        parser.add_argument(arg[0], **arg[1])
    return parser

def main() -> str:
    parser = init_parser()
    args = parser.parse_args()

    match args.generate:
        case 'gherkin':
            if not args.user_case:
                parser.error("--user-case deve ser fornecido quando generate é 'gherkin'")
            else:
                handle_gherkin(args.user_case, args.output_path)

        case 'xunit':
            if not args.feature_path:
                parser.error("--feature deve ser fornecida quando generate é 'xunit'")
            else:
                handle_xunit(args.feature_path, args.output_path)
        
        case 'cypress':
            if not args.vue_path:
                parser.error("--vue_path deve ser fornecida quadno generate é cypress")
            else:
                handle_cypress(args.vue_path, args.output_path)
        
        case 'unit':
            if not args.absolute_path:
                parser.error("--absolute-path é obrigatório quando generate é unit")
            else:
                handle_unit(args.absolute_path, args.output_path)

        case _:
            print("Nenhum parâmetro encontrado")


if __name__ == "__main__":
    main()