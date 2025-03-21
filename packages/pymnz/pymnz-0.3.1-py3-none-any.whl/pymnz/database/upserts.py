from .updates import update_table_from_dataframe
from .inspections import table_exists
from .changes import unique_column, id_autoincrement


def upsert_table_database(
    df, conn, table_name: str, key_col: str, chunk_size: int = 500
) -> int:
    """
    Insere ou atualiza registros de cercas na web.

    :param df: pandas.DataFrame contendo os dados a serem inseridos
    ou atualizados.
    :param conn: Conexão ativa com o banco de dados.
    :return: Número de linhas afetadas ou None.
    """

    # Importar somente quando necessário
    import pandas as pd

    # Verificar se a coluna de chave primária existe
    if key_col not in df.columns:
        raise ValueError(f"A coluna '{key_col}' não existe no DataFrame")

    # Substituir valores NaN por None
    df = df.where(pd.notna(df), None)

    # Verifica se a tabela existe
    if not table_exists(conn, table_name):

        # Criar tabela usando pandas.to_sql
        df.to_sql(
            table_name,
            conn,
            if_exists='replace',
            index=False,
            chunksize=chunk_size,
        )

        # Definir uma coluna id com autoincrement
        id_autoincrement(conn, table_name)

        # Definir coluna key unique
        unique_column(conn, table_name, key_col)

        return len(df)  # Número de linhas inseridas

    # Atualizar a tabela existente em chunks
    chunksize = chunk_size

    # Para rastrear o total de linhas afetadas
    total_rows_affected = 0

    # Iterar sobre os chunks do DataFrame
    for start in range(0, len(df), chunksize):
        # Separar chunk
        chunk = df.iloc[start:start + chunksize]

        # Atualizar chunk
        rows_affected = update_table_from_dataframe(
            chunk, table_name, key_col, conn
        )

        # Somar as linhas afetadas
        total_rows_affected += rows_affected

    return total_rows_affected
