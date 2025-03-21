from pymnz.utils import replace_invalid_values


def update_table_from_dataframe(
    df,
    table_name: str,
    primary_key: str,
    conn
) -> int:
    """
    Atualiza uma tabela no banco de dados MySQL com base em um DataFrame.

    :param df: pandas.DataFrame contendo os dados a serem atualizados.
    :param table_name: Nome da tabela no banco de dados.
    :param primary_key: Nome da coluna que é a chave primária ou índice único.
    :param conn: Conexão ativa com o banco de dados via SQLAlchemy.
    :return: Número de linhas atualizadas.
    """

    # Importar somente quando necessário
    from sqlalchemy import text

    if primary_key not in df.columns:
        raise ValueError(f"A coluna '{primary_key}' não existe no DataFrame.")

    # Gerar a lista de colunas e preparar os placeholders para SQL
    columns = list(df.columns)
    placeholders = ", ".join([f":{col}" for col in columns])
    update_placeholders = ", ".join([
        f"{col}=VALUES({col})" for col in columns if col != primary_key
    ])

    # Query dinâmica
    query = text(f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_placeholders};
    """)

    # Extrair os valores do DataFrame como uma lista de dicionários
    values = df.to_dict(orient="records")

    # Substituir valores indesejados por None
    values = replace_invalid_values(values)

    # Executar a query em massa com SQLAlchemy
    # Passa o texto da query e os valores
    conn.execute(query, values)
    conn.commit()

    return len(df)
