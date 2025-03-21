from typing import List
from pathlib import Path
import pickle
from multiprocessing import Process
import time

from tqdm import tqdm
import pandas as pd
import numpy as np

from charylutokenizer.charylutokenizer import CharyluTokenizer


def tokenize_partition(
    partition_ref: str, partition_num: int, nome_base: str, tokenizer: CharyluTokenizer
):
    root_path = Path("/media/luis/BIGGER/datasets/nlp_datasets/export")
    metadata_folder = root_path / "tokenized_metadata"
    if not metadata_folder.exists():
        metadata_folder.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_folder / f"{nome_base}_{partition_num}.pq"
    if metadata_path.exists():
        return

    binary_folder = root_path / "tokenized_512" / nome_base
    if not binary_folder.exists():
        binary_folder.mkdir(parents=True, exist_ok=True)

    binary_path = binary_folder / f"{nome_base}_{partition_num}.npz"
    if binary_path.exists():
        return

    texts = pd.read_parquet(partition_ref)
    chunks = []

    tokenized = []
    tokens_count = 0
    for _, row in texts.iterrows():
        texto = row.text
        # tokeniza adicionando so o fim, o comeco vai vir depois
        tokenized += tokenizer.tokenize(texto) + [2]
        while len(tokenized) > 511:
            chunk = np.array(
                [1] + tokenized[:511]
            )  # adiciona o comeco aqui para o retroMAE
            chunks.append(chunk)
            tokens_count += 512
            tokenized = tokenized[511:]

    # no final guarda o que sobrou, adicionando padding ja
    tokenized = [1] + tokenized
    diff = 512 - len(tokenized)
    tokenized += [0 for _ in range(diff)]
    chunks.append(np.array(tokenized))
    tokens_count += 512

    # empilha os chunks
    chunks = np.vstack(chunks, dtype=int)
    # salva bonitinho
    np.savez_compressed(binary_path.as_posix(), chunks)
    # adiciona a referencia nos metadados
    metadados = {
        "partition_ref": [partition_ref],
        "tokenized_512_ref": [binary_path.as_posix()],
        "num_tokens": [tokens_count],
    }
    metadados = pd.DataFrame(metadados)
    metadados.to_parquet(metadata_path.as_posix())


if __name__ == "__main__":
    # tokenizer = CharyluTokenizer(
    #     tokenizer_path="/home/luis/projetos/luis_transformers/artifacts/charylu_nocode/tokenizer_2024_90k.json"
    # )

    # df = pd.read_parquet(
    #     "/media/luis/BIGGER/datasets/nlp_datasets/metadata/all_metadata_nodup_lang.pq"
    # )

    # df = df[df.duplicado_80 == 0].reset_index(drop=True)
    # df = df[df.lang.isin(["pt", "en", "fr", "it", "es"])].reset_index(drop=True)
    # df = df[df.tipo != "code"].reset_index(drop=True)
    # partition_num = 0
    # processos = []
    # ja_foi = set()
    # for _, row in tqdm(df.iterrows(), total=len(df)):
    #     partition = row.partition_ref
    #     nome_base = row.base
    #     if partition not in ja_foi:
    #         processos.append(
    #             Process(
    #                 target=tokenize_partition,
    #                 args=(partition, partition_num, nome_base, tokenizer),
    #             )
    #         )
    #         partition_num += 1
    #         ja_foi.add(partition)

    # df = None
    # del df

    # run_pool_of_processes(
    #     estoque_processos=processos,
    #     num_workers=32,
    #     timeout_delaying_process=True,
    #     process_timeout=60 * 30,
    # )

    # agora junta todos os metadados
    todos = []
    for p in Path(
        "/media/luis/BIGGER/datasets/nlp_datasets/export/tokenized_metadata"
    ).glob("*.pq"):
        todos.append(pd.read_parquet(p.as_posix()))
    todos = pd.concat(todos).reset_index(drop=True)

    def nome_base(p):
        p = Path(p)
        return p.parent.stem

    todos["base"] = todos.partition_ref.apply(lambda x: nome_base(x))
    todos.to_parquet(
        "/media/luis/BIGGER/datasets/nlp_datasets/export/tokenized_metadata.pq"
    )
