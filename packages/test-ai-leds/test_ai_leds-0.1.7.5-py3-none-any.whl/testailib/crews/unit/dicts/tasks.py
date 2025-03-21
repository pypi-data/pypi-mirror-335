def create_analyze_code_task(cs_file_content: str):
    return dict(
        description=(
            f"Analise o conteúdo do arquivo .cs:\n{cs_file_content}\n"
            "Identifique quaisquer arquivos adicionais necessários para construir corretamente testes unitários para a classe analisada. "
            "Isso inclui classes dependentes e arquivos contendo implementações usadas no código analisado. "
            "Se nenhuma dependência for encontrada, o retorno deve ser estritamente uma lista de strings sem qualquer formatação adicional, apenas os nomes dos arquivos .cs. "
            "Não retorne JSON, texto extra, explicações ou qualquer outra estrutura de dados."
        ),
        expected_output=(
            "A saída deve ser estritamente uma lista de nomes de arquivos .cs, sem qualquer formatação adicional. "
            "Exemplo correto: [\"FileName.cs\", \"FileName2.cs\"]. "
            "Se nenhuma dependência for encontrada, retorne exatamente: []. "
            "Não inclua texto adicional, JSON, explicações ou qualquer outro formato. Apenas uma lista válida."
        ),
    )

def create_generate_test_task(cs_file_content: str, related_files_content: str, existing_test_content: str):
    return dict(
        description=(
            f"Com base no código C# fornecido e nos testes existentes que já estão APROVADOS, crie testes unitários adicionais seguindo EXATAMENTE o mesmo padrão. "
            "O objetivo é garantir uma cobertura abrangente de todos os cenários possíveis para métodos tanto no Service (CRUD) quanto no Domain (funções). "
            "Mesmo que haja testes existentes para operações como Create, por exemplo, você deve criar mais testes para explorar todas as variações de cenários possíveis, "
            "como casos de sucesso, falhas, validações de borda, e comportamentos excepcionais.\n\n"
            
            "### Código principal:\n"
            f"{cs_file_content}\n\n"
            
            "### Classes auxiliares relacionadas:\n"
            f"{related_files_content}\n\n"
            
            "### TESTES EXISTENTES E APROVADOS - USE COMO MODELO:\n"
            f"{existing_test_content if existing_test_content else 'Não há testes existentes para referência.'}\n\n"
            
            "### REGRAS FUNDAMENTAIS\n"
            "1. **PADRÕES CRÍTICOS PARA REPOSITORY MOCKS**\n"
            "   Para métodos que usam Include():\n"
            "   ```csharp\n"
            "   // CORRETO:\n"
            "   _repositoryMock.Setup(r => r.GetById(id)\n"
            "       .Include(x => x.VersaoModalidadesBolsas))\n"
            "       .Returns((Microsoft.EntityFrameworkCore.Query.IIncludableQueryable<Entity, ICollection<Navigation>>)\n"
            "           Task.FromResult(entity));\n"
            
            "   // Para DeleteRange:\n"
            "   _repositoryMock.Setup(r => r.DeleteRange(It.IsAny<ICollection<Entity>>()))\n"
            "       .Returns(Task.CompletedTask);\n"
            
            "   // Para métodos async:\n"
            "   _repositoryMock.Setup(r => r.AsyncMethod(It.IsAny<params>()))\n"
            "       .Returns(Task.FromResult(expectedResult));\n"
            "   ```\n"
            "2. **TIPOS CORRETOS PARA ENTITY FRAMEWORK**\n"
            "   - Sempre use cast explícito para IIncludableQueryable quando usar Include()\n"
            "   - Para coleções, use ICollection<T> ao invés de List<T>\n"
            "   - Para métodos async, sempre wrap com Task.FromResult() ou Task.CompletedTask\n"
            "   - **EVITE USAR ReturnAsync**: Em vez disso, utilize Task.FromResult() para métodos assíncronos. Isso garante maior consistência e evita problemas comuns de implementação.\n"
            
            "3. **TRATAMENTO DE INCLUDES**\n"
            "   Se o método original usa Include(), seu mock DEVE incluir:\n"
            "   - O mesmo padrão de Include()\n"
            "   - Cast correto para IIncludableQueryable\n"
            "   - Tipo correto para a navegação (ICollection<T>)\n"
            "4. **ERROS COMUNS A EVITAR**\n"
            "   - NÃO use Returns() sem Task.FromResult para métodos async\n"
            "   - NÃO esqueça de fazer cast para IIncludableQueryable\n"
            "   - NÃO use tipos concretos (List<T>) onde interfaces (ICollection<T>) são esperadas\n"
            "   - **CONSULTE SEMPRE A CLASSE PRINCIPAL E AS CLASSES AUXILIARES**: Antes de escrever os testes, verifique cuidadosamente os tipos de entrada e saída das funções/métodos. "
            "     Certifique-se de que os dados utilizados nos testes estejam convertidos corretamente para os tipos esperados. Por exemplo, se um método aceita um tipo específico de classe, "
            "     não passe diretamente um objeto de outro tipo sem conversão adequada. Caso encontre incompatibilidades, tente encontrar alternativas ou ajustes que mantenham a integridade do teste.\n"
            
            "### EXEMPLOS DE MOCKS COMPLEXOS:\n"
            "```csharp\n"
            "// Exemplo 1: GetById com Include\n"
            "_repositoryMock.Setup(r => r.GetById(id)\n"
            "    .Include(x => x.NavigationProperty))\n"
            "    .Returns((Microsoft.EntityFrameworkCore.Query.IIncludableQueryable<Entity, ICollection<Navigation>>)\n"
            "        Task.FromResult(entity));\n\n"
            
            "// Exemplo 2: Delete com múltiplas operações\n"
            "_repositoryMock.Setup(r => r.Delete(It.IsAny<Entity>()))\n"
            "    .Returns(Task.CompletedTask);\n"
            "_repositoryMock.Setup(r => r.DeleteRange(It.IsAny<ICollection<Navigation>>()))\n"
            "    .Returns(Task.CompletedTask);\n"
            "```\n"
            
            "### EXEMPLOS DE ADAPTAÇÃO:\n"
            "Se existe um teste 'Create_Success', use-o como base para 'Update_Success':\n"
            "1. Copie a estrutura completa\n"
            "2. Ajuste os dados de entrada\n"
            "3. Modifique as configurações de mock mantendo o padrão\n"
            "4. Adapte as assertions conforme necessário\n"
            
            "### PRIORIDADES:\n"
            "1. Manter os testes existentes intactos\n"
            "2. Reutilizar padrões aprovados\n"
            "3. Cobrir métodos sem testes\n"
            "4. Garantir casos de sucesso e erro\n"
            
            "### LEMBRE-SE:\n"
            "- Os testes existentes são seu guia principal\n"
            "- Quando em dúvida, procure um teste similar e adapte\n"
            "- Mantenha a consistência com o que já funciona\n"
            "- Mesmo que haja testes para operações básicas (ex.: Create), expanda-os para cobrir cenários adicionais, como validações de borda, entradas inválidas, e comportamentos excepcionais\n"
            "- No mínimo, devem ser criados 30 testes para garantir uma cobertura robusta. Isso inclui testes tanto para o Service (CRUD) quanto para o Domain (funções específicas)\n"
            "- Consulte sempre a classe principal e as classes auxiliares para evitar erros básicos, especialmente relacionados a conversões de tipos. Se um método/função aceitar um tipo específico de classe, "
            "  certifique-se de que os dados fornecidos nos testes estejam convertidos corretamente. Caso encontre dificuldades, busque alternativas ou ajustes que mantenham a integridade do teste.\n"
        ),
        expected_output=(
            "Um arquivo C# contendo todos os testes existentes mais os novos testes, "
            "onde os novos seguem EXATAMENTE os mesmos padrões dos existentes, "
            "apenas adaptando dados e assertions conforme necessário. "
            "O resultado final deve incluir no mínimo 30 testes, cobrindo cenários de sucesso, falha, validações de borda e comportamentos excepcionais, "
            "tanto para operações no Service (CRUD) quanto no Domain (funções específicas). "
            "Certifique-se de que os testes evitem o uso de ReturnAsync e sigam rigorosamente as regras de conversão de tipos, consultando a classe principal e as classes auxiliares para evitar erros básicos."
        ),
    )