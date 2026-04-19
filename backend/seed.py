"""
Seed de demonstração do Sumé — 3 casos controlados para o Dia 5.

Casos:
  1. Ana Costa    — trabalho limpo (sem falsos positivos)
  2. Bruno Lopes  — trabalho com marcadores de IA + fontes fabricadas
  3. Carla Mendes — evolução legítima ao longo do tempo

Uso (na pasta backend, com venv ativo e docker rodando):
  python seed.py           # limpa e reinserere os 3 casos
  python seed.py --limpar  # só limpa sem reinserir
"""

import asyncio
import sys
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import delete

load_dotenv()

import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sume:sume@localhost:5432/sume")

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
engine = create_async_engine(DATABASE_URL, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)

from app.database import Base
from app.models.turma import Turma
from app.models.aluno import Aluno
from app.models.trabalho import Trabalho, TrabalhoFeature
from app.models.perfil import PerfilAluno
from app.models.dossie import Dossie, Desfecho
from app.models.gdocs import HistoricoVersao
from app.services.features import extrair_features
from app.services.perfil import recalcular_perfil


# ── Helpers ───────────────────────────────────────────────────────────────────

def dt(ano: int, mes: int, dia: int) -> datetime:
    return datetime(ano, mes, dia)


# ── Textos ────────────────────────────────────────────────────────────────────
#
# Parágrafos separados por \n\n — igual ao que o parser gera a partir de .docx/.pdf.
# Cada grupo tem textos de baseline (_B1, _B2, …) e um trabalho a testar (_NOVO).


# ─── ANA COSTA — redações de 8º ano, estilo simples e consistente ─────────────

ANA_B1 = """\
O Pantanal é a maior área úmida do mundo. Ele fica no centro do Brasil. \
Tem muitos animais como onças, jacarés e capivaras. Eu acho muito bonito esse lugar. \
A gente precisa cuidar da natureza.

O desmatamento é um problema sério. Quando cortam as árvores os animais perdem o lugar \
para morar. Também acontece enchentes quando não tem vegetação. Isso é ruim para todos.

Eu acho que devemos preservar o Pantanal. O governo precisa fazer mais leis. \
E a gente pode ajudar não jogando lixo. Todo mundo tem que fazer a sua parte."""

ANA_B2 = """\
A reciclagem é muito importante para o meio ambiente. Com ela podemos reutilizar \
materiais como papel, vidro e plástico. Isso ajuda a reduzir o lixo nos aterros. \
Eu acho que todo mundo devia reciclar.

Na minha casa a gente separa o lixo. Tem uma lixeira para o orgânico e outra para \
o reciclável. É fácil de fazer e ajuda muito o planeta. \
Minha mãe me ensinou a fazer isso quando era pequena.

Nas escolas também podia ter mais educação ambiental. Os professores podem falar mais \
sobre reciclagem. Assim as crianças aprendem desde cedo a cuidar do meio ambiente. \
É importante para o futuro."""

ANA_B3 = """\
A tecnologia mudou muito a nossa vida. Hoje em dia todo mundo usa celular e computador. \
Eu uso o celular para estudar e falar com os amigos. A internet tem muita informação útil.

Mas a tecnologia também tem lados ruins. As pessoas ficam viciadas no celular. \
Às vezes a gente fica mais tempo no telefone do que conversando com a família. \
Isso não é bom para os relacionamentos.

Eu acho que precisamos usar a tecnologia de forma equilibrada. Tem que ter hora para \
usar o celular e hora para descansar. Os pais precisam ajudar as crianças a fazer isso. \
Com disciplina dá para aproveitar o que a tecnologia tem de bom."""

# Trabalho da Ana — tema diferente, mesmo estilo → deve passar sem alertas
ANA_NOVO = """\
O cerrado é um dos biomas mais importantes do Brasil. Ele cobre quase um quarto do \
território nacional. Tem muitas plantas e animais que só existem lá. \
Eu acho que as pessoas não conhecem muito bem o cerrado.

O cerrado está em perigo por causa da agricultura. Cada vez mais fazendas tomam o lugar \
do cerrado. Os animais ficam sem lugar para viver. Isso é um problema que precisa de solução.

Algumas pessoas trabalham para proteger o cerrado. Tem reservas ambientais e parques \
nacionais que são muito importantes. Mas ainda precisa de mais proteção.

Eu acho que o governo e a sociedade devem trabalhar juntos. Precisamos de mais \
conscientização sobre o cerrado. E também de leis mais rígidas para proteger esse bioma. \
Assim podemos preservar essa riqueza para as próximas gerações."""


# ─── BRUNO LOPES — baseline simples, trabalho "gerado" ────────────────────────
#
# O texto BRUNO_IA usa palavras de AI_PALAVRAS (features.py) em suas formas exatas,
# frases longas, parágrafos de tamanho similar e fontes inexistentes (DOI + URL),
# para garantir desvios visíveis e fontes vermelhas/amarelas no demo.

BRUNO_B1 = """\
Os animais são seres vivos muito importantes. Eles vivem em vários lugares do mundo. \
Tem animais na terra, na água e no ar. Eu gosto muito de animais, especialmente cachorros.

Os animais precisam de cuidado. Eles merecem respeito e amor. \
Não pode maltratar animal, isso é crime. A gente deve proteger os animais.

Tem muitos animais em extinção hoje. Isso é culpa do homem. \
O desmatamento e a caça são problemas graves. Precisamos parar com isso."""

BRUNO_B2 = """\
A escola é um lugar muito importante. A gente aprende muitas coisas na escola. \
Aprende a ler, escrever e fazer conta. Também faz amigos na escola.

Eu gosto da escola mas às vezes é difícil. Tem dias que a lição é muito complicada. \
Mas a professora explica e ajuda. Com esforço a gente consegue aprender.

A escola prepara a gente para o futuro. Sem estudar fica difícil conseguir emprego. \
Por isso é importante ir à escola todo dia. E prestar atenção nas aulas."""

BRUNO_B3 = """\
O esporte faz bem para a saúde. Quando a gente pratica esporte fica mais saudável. \
O coração funciona melhor e os músculos ficam fortes. É bom para o corpo e para a mente.

Eu pratico futebol com os amigos. A gente joga no campo perto de casa. \
É muito divertido e faz amizades. Gosto muito de jogar futebol.

Todo mundo devia praticar algum esporte. Pode ser futebol, natação ou vôlei. \
O importante é se movimentar. Fica muito mais saudável quem pratica esporte regularmente."""

# Palavras de AI_PALAVRAS usadas: ademais, outrossim, fundamental, primordial,
# perpassa, indubitavelmente, basilar, nortear, corrobora, elucida, multifacetado,
# imprescindível, inegável, inequivocamente.
# Fontes: DOI fictício (vai falhar no CrossRef) + URL 404 + citação inline não encontrável.
BRUNO_IA = """\
A problemática ambiental que perpassa a questão do desmatamento da Amazônia \
configura-se, indubitavelmente, como um dos mais basilar desafios hodierno \
enfrentados pela sociedade contemporânea, visto que as consequências multifacetado \
desse fenômeno impactam não apenas o ecossistema regional, mas o equilíbrio climático \
global como um todo, tornando fundamental compreender os múltiplos vetores que corrobora \
para a aceleração desse processo devastador e irreversível.

Ademais, é primordial ressaltar que os mecanismos de governança ambiental vigentes \
mostram-se insuficientes para nortear de maneira eficaz a preservação dos recursos \
naturais amazônicos. Outrossim, a ausência de políticas públicas integradas constitui \
um entrave crucial à proteção desse patrimônio ecológico inestimável, conforme elucida \
Silva, João Carlos (2023) ao analisar os dados de degradação dos últimos cinco anos, \
exigindo uma resposta institucional imediata, abrangente e estruturada.

De forma inequivocamente necessária, a solução para essa problemática demanda uma \
abordagem sistêmica e multidisciplinar que articule os diferentes atores sociais. \
Segundo dados disponíveis em https://www.relatorio-amazonia-inexistente.com.br/dados2023, \
a taxa de desmatamento cresceu exponencialmente, e o DOI 10.9999/amazonia-ficticia.2023.001 \
aponta que a recuperação das áreas degradadas requer investimentos substanciais e \
comprometimento político de longo prazo para ser efetivada com sucesso.

Em suma, a preservação da floresta amazônica constitui um imperativo ético e \
civilizacional que transcende fronteiras nacionais. É imprescindível que os atores \
sociais, econômicos e políticos articulem-se de maneira propositiva para enfrentarem \
esse desafio de magnitude global. A inércia diante dessa realidade representa, de forma \
inegável e inequivocamente demonstrada, uma ameaça à própria sustentabilidade da vida."""


# ─── CARLA MENDES — quatro baselines mostrando evolução gradual ───────────────

CARLA_B1 = """\
O lixo é um problema muito grande. Tem muito lixo nas ruas e nos rios. \
Isso faz mal para o meio ambiente. Precisamos jogar o lixo no lugar certo.

Eu acho que as pessoas não se preocupam com o lixo. Jogam no chão sem pensar. \
Isso é errado. Tem que mudar esse costume.

Se todo mundo jogar o lixo na lixeira vai ficar melhor. A cidade vai ficar mais limpa. \
Os animais vão ficar mais seguros. É simples mas funciona."""

CARLA_B2 = """\
A água é muito importante para a vida. Sem água a gente não sobrevive. \
Mas muita gente desperdiça água sem perceber. Isso é um problema que precisamos resolver.

No mundo inteiro tem falta de água limpa para muitas pessoas. \
Muitas pessoas não têm acesso à água potável, o que é uma injustiça grave. \
O governo precisa resolver esse problema com políticas públicas bem planejadas.

Em casa a gente pode economizar água no dia a dia. Fecha a torneira quando não está \
usando. Toma banho mais rápido. Essas atitudes simples fazem diferença quando \
todo mundo as pratica."""

CARLA_B3 = """\
O desmatamento é um dos maiores problemas ambientais que temos hoje em dia. \
Quando as florestas são derrubadas, muitos animais perdem seus habitats naturais. \
Além disso, as árvores são fundamentais para absorver o gás carbônico e regular o clima. \
Por isso, é essencial que a sociedade se preocupe com essa questão ambiental urgente.

No Brasil, o desmatamento acontece principalmente na Amazônia e no Cerrado. \
A expansão da agricultura e da pecuária são as principais causas desse problema crescente. \
Também tem a extração ilegal de madeira, que prejudica muito os ecossistemas naturais. \
O governo precisa fiscalizar melhor essas atividades e aplicar punições mais severas.

Mas não é só o governo que pode agir sobre esse problema complexo. \
As empresas também têm responsabilidade social e ambiental perante a sociedade. \
Elas precisam adotar práticas mais sustentáveis em toda a sua cadeia produtiva. \
E os consumidores podem escolher produtos de empresas que respeitam o meio ambiente."""

CARLA_B4 = """\
A questão energética representa um dos principais desafios do desenvolvimento \
sustentável no século XXI. Com o crescimento da população mundial e o aumento \
constante da demanda por energia, torna-se cada vez mais necessário buscar alternativas \
limpas e renováveis que causem menos impacto ambiental do que os combustíveis fósseis.

A transição para uma matriz energética mais limpa, no entanto, não é simples nem rápida. \
Ela exige investimentos significativos em infraestrutura, pesquisa e desenvolvimento \
tecnológico. Também requer mudanças profundas nas políticas públicas e na regulação do \
setor energético, além de uma transformação cultural na forma como a sociedade consome.

No contexto brasileiro, a energia hidrelétrica ainda domina a matriz elétrica, \
mas apresenta limitações importantes, como a dependência das chuvas e o impacto \
socioambiental sobre os rios e comunidades ribeirinhas afetadas. Por isso, diversificar \
as fontes de energia é fundamental para garantir segurança energética e reduzir os \
impactos ambientais no longo prazo."""

# Trabalho novo da Carla — mais elaborado, mas alinhado com a trajetória projetada
CARLA_NOVO = """\
As mudanças climáticas constituem um fenômeno complexo que afeta profundamente os \
ecossistemas e as sociedades humanas em todo o mundo. O aumento das temperaturas \
globais, provocado principalmente pela emissão de gases de efeito estufa, tem gerado \
consequências cada vez mais visíveis, como o derretimento das geleiras e a elevação \
do nível dos oceanos, exigindo respostas urgentes de governos e cidadãos em todo o planeta.

No Brasil, os efeitos das mudanças climáticas já se fazem sentir de diversas maneiras \
distintas em cada região. A região Nordeste enfrenta períodos de seca cada vez mais \
prolongados, comprometendo a segurança hídrica e alimentar de milhões de pessoas. \
Por outro lado, regiões Sul e Sudeste têm registrado chuvas mais intensas e enchentes \
frequentes, causando danos materiais e humanos consideráveis em várias cidades.

A solução para as mudanças climáticas passa necessariamente por uma transformação \
profunda nos modelos de produção e consumo consolidados nas últimas décadas. \
A descarbonização da economia, por meio da substituição gradual dos combustíveis \
fósseis por fontes renováveis, é um caminho indispensável para conter o aquecimento. \
Além disso, é preciso investir na preservação e restauração dos biomas naturais, \
que funcionam como importantes sumidouros de carbono e reservatórios de biodiversidade."""


# ── Catálogo de dados ─────────────────────────────────────────────────────────

TURMA = {"nome": "8º Ano A", "disciplina": "Língua Portuguesa", "ano_serie": "8º Ano"}

ALUNOS = [
    {"nome": "Ana Costa",    "matricula": "2024001"},
    {"nome": "Bruno Lopes",  "matricula": "2024002"},
    {"nome": "Carla Mendes", "matricula": "2024003"},
]

# (texto, tipo, eh_baseline, data_entrega, titulo)
TRABALHOS: list[list[tuple]] = [
    [   # Ana
        (ANA_B1,   "redação", True,  dt(2024, 2, 12), "O Pantanal e a preservação ambiental"),
        (ANA_B2,   "redação", True,  dt(2024, 4,  8), "A importância da reciclagem"),
        (ANA_B3,   "redação", True,  dt(2024, 6,  3), "Tecnologia no cotidiano"),
        (ANA_NOVO, "redação", False, dt(2024, 9, 16), "O bioma Cerrado"),
    ],
    [   # Bruno
        (BRUNO_B1, "redação", True,  dt(2024, 2, 14), "Os animais e a natureza"),
        (BRUNO_B2, "redação", True,  dt(2024, 4, 10), "A importância da escola"),
        (BRUNO_B3, "redação", True,  dt(2024, 6,  5), "Esporte e saúde"),
        (BRUNO_IA, "redação", False, dt(2024, 9, 18), "Desmatamento da Amazônia"),
    ],
    [   # Carla
        (CARLA_B1,   "redação", True,  dt(2024, 2, 10), "O problema do lixo"),
        (CARLA_B2,   "redação", True,  dt(2024, 4,  6), "A crise da água"),
        (CARLA_B3,   "redação", True,  dt(2024, 6,  1), "Desmatamento e seus impactos"),
        (CARLA_B4,   "redação", True,  dt(2024, 7, 20), "A questão energética"),
        (CARLA_NOVO, "redação", False, dt(2024, 9, 20), "Mudanças climáticas e seus efeitos"),
    ],
]


# ── Limpeza ───────────────────────────────────────────────────────────────────

async def limpar(db: AsyncSession) -> None:
    from app.models.trabalho import TrabalhoFeature, Fonte, ParagrafoDestacado

    print("Limpando dados anteriores…")
    for Model in (Desfecho, Dossie, ParagrafoDestacado, Fonte,
                  TrabalhoFeature, HistoricoVersao, PerfilAluno, Trabalho, Aluno, Turma):
        await db.execute(delete(Model))
    await db.commit()
    print("Banco limpo.\n")


# ── Seed ──────────────────────────────────────────────────────────────────────

async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with Session() as db:
        await limpar(db)

        turma = Turma(**TURMA)
        db.add(turma)
        await db.flush()
        print(f"Turma: {turma.nome} (id={turma.id})")

        for aluno_dados, trabalhos_lista in zip(ALUNOS, TRABALHOS):
            aluno = Aluno(**aluno_dados, turma_id=turma.id)
            db.add(aluno)
            await db.flush()
            print(f"\n  {aluno.nome} (id={aluno.id})")

            for texto, tipo, eh_baseline, data, titulo in trabalhos_lista:
                trabalho = Trabalho(
                    aluno_id=aluno.id,
                    titulo=titulo,
                    tipo=tipo,
                    texto=texto,
                    formato_origem="seed",
                    baseline=eh_baseline,
                    data_entrega=data,
                )
                db.add(trabalho)
                await db.flush()

                for nome, valor in extrair_features(texto).items():
                    db.add(TrabalhoFeature(
                        trabalho_id=trabalho.id,
                        nome=nome,
                        valor=valor,
                    ))

                tag = "[baseline]" if eh_baseline else "[TESTE]   "
                print(f"    {tag} id={trabalho.id}  {titulo}")

            await db.commit()
            await recalcular_perfil(aluno.id, db)
            print(f"    → Perfil recalculado ({sum(1 for _, _, b, *_ in trabalhos_lista if b)} baselines)")

    print("\n✓ Seed concluído.")
    print("\nPróximos passos (use o id do trabalho [TESTE] acima):")
    print("  Ana  (limpo)     → POST /analise/{id}")
    print("  Bruno (IA)       → POST /analise/{id} → POST /fontes/{id} → POST /relatorio/{id}")
    print("  Carla (evolução) → POST /analise/{id}")
    print("\nSwagger: http://localhost:8001/docs")


# ── Entrypoint ────────────────────────────────────────────────────────────────

async def main() -> None:
    if "--limpar" in sys.argv:
        async with Session() as db:
            await limpar(db)
    else:
        await seed()


if __name__ == "__main__":
    asyncio.run(main())
