"""
Seed de dados de demonstração do Sumé.

Cria 3 alunos com baselines e trabalhos para os casos de demo:
  - Ana Souza    → trabalho limpo (sem flags)
  - Bruno Lima   → trabalho com padrão de IA (flags claros)
  - Carla Mendes → evolução legítima (trajetória funcionando)

Uso (com venv ativado, dentro de /backend):
    python seed_dados.py
"""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sume:sume@localhost:5432/sume")
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

from app.database import Base
from app.models.turma import Turma
from app.models.aluno import Aluno
from app.models.trabalho import Trabalho, TrabalhoFeature
from app.services.features import extrair_features

# ---------------------------------------------------------------------------
# Textos — ANA SOUZA (escrita simples e consistente, SEM IA)
# ---------------------------------------------------------------------------

ANA_BASELINE_1 = """\
A água é muito importante pra vida. Sem ela os seres vivos não conseguem sobreviver. A gente usa água pra tomar banho, cozinhar, beber e limpar as coisas.

No Brasil tem muitos rios e lagos. O rio Amazonas é o maior do mundo em volume de água. Mas mesmo tendo tanta água, em algumas regiões as pessoas sofrem com a seca.

O desmatamento é um dos problemas que afeta os rios. Quando as árvores são cortadas, o solo fica sem proteção e a água da chuva leva a terra pra dentro dos rios. Isso deixa a água suja e prejudica os peixes e as plantas.

Pra economizar água em casa, a gente pode fechar a torneira enquanto escova os dentes e tomar banhos mais curtos. Essas atitudes simples fazem diferença quando todo mundo faz junto.

Na escola aprendemos que a água doce que pode ser usada pelas pessoas é muito pouca. A maior parte da água da Terra é salgada e fica nos oceanos. Por isso é tão importante cuidar dos rios e dos lençóis freáticos.

Eu acho que as pessoas precisam se conscientizar mais sobre o assunto. Muita gente desperdiça água sem perceber. As crianças precisam aprender desde cedo como preservar esse recurso tão importante pra vida.

Se todo mundo fizer a sua parte, a gente consegue garantir que as próximas gerações também vão ter acesso à água limpa. É uma responsabilidade de todos nós, não só do governo.
"""

ANA_BASELINE_2 = """\
O desmatamento é um problema muito sério no Brasil e no mundo. Quando as florestas são derrubadas, os animais perdem seus habitats e muitas espécies podem até desaparecer.

Na Amazônia, muitas árvores são cortadas por causa da pecuária e da agricultura. Os fazendeiros derrubam a mata pra plantar soja ou criar gado. Isso causa muito prejuízo pro meio ambiente.

As árvores também são importantes porque elas absorvem o gás carbônico do ar e liberam oxigênio. Quando a gente destrói uma floresta, esse ciclo é interrompido e o efeito estufa aumenta.

As queimadas são outro problema que acontece muito durante a seca. O fogo destrói tudo muito rápido e é difícil de controlar. Depois que uma área é queimada, demora muitos anos pra vegetação crescer de novo.

O governo tem leis que protegem as florestas, como o Código Florestal. Mas nem sempre essas leis são respeitadas. Fiscalizar uma área tão grande como a Amazônia é muito difícil.

As pessoas podem ajudar consumindo produtos de empresas que não desmatam e apoiando projetos de reflorestamento. Pequenas atitudes do dia a dia também fazem diferença, como reciclar o lixo e não desperdiçar papel.

Eu acredito que educar as crianças sobre a importância das florestas é fundamental pra mudar essa situação. Quando a gente entende por que as árvores são importantes, fica mais fácil querer protegê-las.
"""

ANA_BASELINE_3 = """\
A reciclagem é uma forma de reaproveitamento dos materiais que já foram usados. Com ela, menos lixo vai parar nos aterros sanitários e menos recursos naturais precisam ser extraídos.

Os materiais que podem ser reciclados são o papel, o plástico, o vidro e o metal. Cada um tem um processo diferente de reciclagem e precisa ser separado do lixo orgânico.

Na maioria das cidades brasileiras existe coleta seletiva. Os caminhões passam em dias específicos recolhendo o material reciclável. Mas muitas pessoas ainda não têm o hábito de separar o lixo.

Quando o lixo é separado certo, ele vai pra usinas de triagem onde os trabalhadores separam o material por tipo. Depois esse material é vendido pra indústrias que fazem novos produtos com ele.

A reciclagem gera empregos principalmente pras cooperativas de catadores. Essas pessoas trabalham coletando material reciclável e ganham dinheiro com a venda dele. É uma atividade que ajuda o meio ambiente e a sociedade ao mesmo tempo.

Em casa, a gente pode começar separando o lixo em dois tipos: o orgânico, que é resto de comida, e o reciclável, que são embalagens e papel. Com o tempo vira um hábito fácil de manter.

Eu acho que as escolas deveriam falar mais sobre reciclagem e dar exemplos práticos pras crianças. Quando a gente aprende cedo, leva esse conhecimento pra vida toda.
"""

ANA_TRABALHO_NOVO = """\
O aquecimento global é um fenômeno que vem preocupando cientistas de todo o mundo. Ele acontece quando a temperatura da Terra aumenta por causa do acúmulo de gases como o dióxido de carbono na atmosfera.

As principais causas do aquecimento global são as atividades humanas. A queima de combustíveis fósseis, como gasolina e carvão, libera muito gás carbônico no ar. As fábricas e os carros são grandes responsáveis por isso.

Com o aumento da temperatura, as geleiras dos polos estão derretendo. Isso faz o nível do mar subir, o que pode inundar cidades costeiras no futuro. Alguns países de ilha já estão sendo afetados por esse problema.

O clima também muda com o aquecimento global. As chuvas ficam mais irregulares, as secas ficam mais longas e as tempestades ficam mais fortes. Isso prejudica a agricultura e pode causar problemas de abastecimento de alimentos.

Pra reduzir o aquecimento global é preciso diminuir a emissão de gases poluentes. Os países precisam usar mais energias renováveis, como a solar e a eólica, e depender menos do petróleo e do carvão.

As pessoas também podem ajudar no dia a dia usando menos o carro, economizando energia em casa e consumindo menos produtos industrializados. Cada escolha faz uma pequena diferença quando feita por muitas pessoas.

Eu acho que o aquecimento global é um problema que precisa de ação urgente. Se a gente não agir agora, as consequências vão ser muito piores pras gerações futuras.
"""

# ---------------------------------------------------------------------------
# Textos — BRUNO LIMA (baseline simples + trabalho com padrão de IA)
# ---------------------------------------------------------------------------

BRUNO_BASELINE_1 = """\
A poluição é muito ruim pro meio ambiente. Ela acontece quando substâncias prejudiciais entram no ar, na água ou no solo.

A poluição do ar vem principalmente dos carros e das fábricas. Eles soltam fumaça que contém gases tóxicos. Quem mora perto de lugares muito poluídos pode ter problemas de saúde como asma.

Os rios também sofrem com a poluição. As fábricas jogam resíduos nos rios e isso mata os peixes. O esgoto das casas também polui a água quando não é tratado.

O lixo jogado no chão também é um problema sério. Ele entope os bueiros e causa enchentes. Além disso fica feio e atrai ratos e baratas.

Pra diminuir a poluição as pessoas precisam mudar seus hábitos. Usar menos o carro, não jogar lixo no chão e cobrar do governo mais fiscalização são formas de ajudar.

Eu acho que é possível ter um mundo mais limpo se cada um fizer sua parte.
"""

BRUNO_BASELINE_2 = """\
A energia solar é uma fonte de energia que vem do sol. Ela é limpa porque não polui o meio ambiente como o petróleo e o carvão.

Os painéis solares captam a luz do sol e transformam em eletricidade. Eles podem ser colocados no telhado das casas. Com isso as pessoas pagam menos de luz.

No Brasil tem muito sol durante o ano todo. Por isso a energia solar é uma boa opção aqui. Alguns estados já têm muitos painéis solares instalados.

O problema é que os painéis são caros pra instalar no começo. Mas com o tempo a economia na conta de luz compensa o investimento.

Eu acho que o governo deveria incentivar mais as pessoas a usar energia solar. Com subsídios ficaria mais fácil pra todo mundo ter acesso.
"""

BRUNO_BASELINE_3 = """\
Os animais em extinção precisam de proteção. Quando uma espécie desaparece, o equilíbrio da natureza é afetado.

No Brasil tem muitos animais ameaçados como a onça pintada e o mico leão dourado. O desmatamento é a principal causa disso porque destrói onde eles vivem.

As unidades de conservação são áreas protegidas pelo governo onde os animais podem viver sem ser perturbados. São parques nacionais e reservas ecológicas.

Projetos de reprodução em cativeiro também ajudam. O mico leão dourado foi salvo assim. Criaram animais em zoológicos e depois soltaram na natureza.

É importante preservar os animais porque cada espécie tem um papel importante na natureza. Quando uma delas some, pode causar problemas em toda a cadeia alimentar.
"""

BRUNO_TRABALHO_IA = """\
A preservação ambiental constitui, indubitavelmente, um dos desafios mais cruciais e multifacetados que a sociedade contemporânea enfrenta no limiar do século XXI. Ademais, a complexidade inerente a essa problemática perpassa diversas esferas do conhecimento humano, demandando uma abordagem interdisciplinar e holística para sua efetiva resolução.

A degradação dos ecossistemas terrestres representa, outrossim, uma ameaça basilar à manutenção da biodiversidade global. Nesse sentido, é fundamental compreender que os impactos antrópicos sobre o meio ambiente transcendem as fronteiras geográficas, configurando-se como uma questão de responsabilidade coletiva e solidariedade internacional. A depleção dos recursos naturais, corroborada por inúmeros estudos científicos de renomadas instituições de pesquisa, evidencia a urgência de medidas mitigatórias eficazes.

No contexto brasileiro, destaca-se a imperativa necessidade de se estabelecer políticas públicas robustas e abrangentes que norteiem a exploração sustentável dos biomas nacionais. A implementação de mecanismos de fiscalização mais eficientes, aliada ao fortalecimento do arcabouço jurídico-normativo vigente, constitui pressuposto indispensável para a consecução dos objetivos estabelecidos nos acordos climáticos internacionais dos quais o Brasil é signatário.

É imprescindível, outrossim, que os atores sociais envolvidos na cadeia produtiva adotem práticas alinhadas aos preceitos do desenvolvimento sustentável. A transição para uma economia de baixo carbono, fundamentada em matrizes energéticas renováveis e tecnologias limpas, representa o caminho mais viável para a conciliação entre crescimento econômico e preservação ambiental. Nesse contexto, a educação ambiental assume papel fulcral na formação de uma consciência ecológica capaz de transformar paradigmas comportamentais arraigados.

Em suma, a preservação ambiental não configura apenas um imperativo ético, mas também uma condição sine qua non para a garantia da qualidade de vida das gerações futuras. A implementação de soluções inovadoras, aliada ao engajamento proativo de todos os segmentos da sociedade, constitui o alicerce fundamental sobre o qual se edificará um futuro verdadeiramente sustentável. (Silva, 2023; Costa et al., 2022; http://meioambientefalso.xyz/artigos/preservacao)
"""

# ---------------------------------------------------------------------------
# Textos — CARLA MENDES (evolução legítima ao longo do tempo)
# ---------------------------------------------------------------------------

CARLA_BASELINE_1 = """\
Os oceanos são muito grandes e cobrem mais da metade da terra. Neles vivem muitos animais como peixe, baleia e tubarão.

A poluição dos oceanos é um problema. As pessoas jogam lixo no mar e isso faz mal pras criaturas marinhas. As tartarugas confundem sacolas plásticas com água viva e comem elas.

O aquecimento da água também afeta os corais. Quando a água esquenta muito os corais ficam brancos. Isso se chama branqueamento e pode matar os corais.

Os oceanos são importantes pra nós também porque regulam o clima da terra e produzem muito do oxigênio que respiramos. Por isso devemos cuidar deles.

Eu acho que deveriam ter mais leis contra jogar lixo no mar e mais fiscalização nas praias e portos.
"""

CARLA_BASELINE_2 = """\
A poluição dos oceanos tem aumentado bastante nos últimos anos. O plástico é um dos maiores vilões porque demora centenas de anos pra se decompor na natureza.

Existe uma área no Oceano Pacífico chamada de ilha de lixo. É uma concentração enorme de plástico que se formou por causa das correntes marítimas. Ela já tem um tamanho parecido com o estado de São Paulo.

Os animais marinhos sofrem muito com esse problema. Além das tartarugas, os peixes também ingerem microplásticos sem querer. Esses fragmentos pequenos ficam em seus organismos e depois chegam até nós quando comemos frutos do mar.

Uma solução que tem ganhado força é a economia circular. A ideia é reduzir a produção de plástico descartável e criar sistemas de reaproveitamento dos materiais. Alguns países já proibiram canudos e sacolas plásticas.

As pessoas podem ajudar recusando plásticos desnecessários, levando sacola retornável nas compras e participando de mutirões de limpeza de praias. Pequenas ações individuais, quando multiplicadas, geram grande impacto coletivo.

Eu acredito que a solução passa tanto por mudanças individuais quanto por políticas públicas mais rígidas. As empresas também precisam se responsabilizar pelos resíduos que geram.
"""

CARLA_BASELINE_3 = """\
A degradação dos oceanos representa um problema ambiental grave que afeta todo o ecossistema marinho e, indiretamente, a vida humana. O descarte inadequado de resíduos plásticos, aliado ao aquecimento global e à sobrepesca, compromete a biodiversidade e os serviços ecossistêmicos que os mares oferecem.

Estudos recentes indicam que cerca de oito milhões de toneladas de plástico chegam aos oceanos anualmente. Esses materiais se fragmentam em microplásticos que penetram na cadeia alimentar e foram detectados até em organismos humanos. A magnitude do problema exige respostas coordenadas em escala global.

No Brasil, o litoral extenso e a rica biodiversidade marinha tornam o país especialmente vulnerável a esses impactos. A Mata Atlântica costeira e os recifes de coral nordestinos são ecossistemas ameaçados que dependem da saúde dos oceanos para sua manutenção.

Iniciativas como o Acordo Global sobre Poluição Plástica, atualmente em negociação nos fóruns internacionais, representam um passo importante na direção certa. Contudo, a implementação efetiva dessas medidas requer comprometimento político real e mecanismos de financiamento acessíveis para os países em desenvolvimento.

A educação ambiental tem papel central na formação de cidadãos conscientes de sua responsabilidade com os oceanos. Quando as pessoas compreendem as conexões entre seus hábitos cotidianos e a saúde dos ecossistemas marinhos, tornam-se agentes de transformação capazes de influenciar tanto o consumo individual quanto as decisões coletivas.

Preservar os oceanos é, portanto, uma responsabilidade compartilhada entre governos, empresas e cidadãos. As gerações futuras dependerão da qualidade das decisões que tomamos hoje.
"""

CARLA_TRABALHO_NOVO = """\
A crise climática e a degradação ambiental configuram os maiores desafios globais do século XXI, exigindo respostas urgentes e articuladas em diferentes escalas. Entre os biomas mais afetados encontra-se o Cerrado brasileiro, segunda maior savana do mundo e um dos hotspots de biodiversidade do planeta.

O Cerrado abriga aproximadamente cinco por cento de toda a biodiversidade terrestre e é responsável por regular o regime hídrico de importantes bacias hidrográficas brasileiras, incluindo a do São Francisco, do Tocantins e do Paraná. Sua vegetação adaptada ao clima sazonal desenvolveu raízes profundas que captam água e a redistribuem para os lençóis freáticos, funcionando como uma esponja natural que abastece rios e nascentes.

A expansão da fronteira agrícola representa a principal ameaça ao bioma. Segundo dados do Instituto Nacional de Pesquisas Espaciais, mais de cinquenta por cento da cobertura original do Cerrado já foi suprimida para dar lugar principalmente à produção de soja e à pecuária extensiva. O ritmo do desmatamento permanece preocupante, especialmente nas regiões onde a fiscalização é menos efetiva.

As consequências dessa perda vão além da biodiversidade. A redução da vegetação nativa impacta diretamente a segurança hídrica de cidades que dependem de mananciais originários do bioma. Estudos indicam correlação entre o avanço do desmatamento e a diminuição da precipitação regional, criando um ciclo de retroalimentação que agrava a vulnerabilidade climática.

Frente a esse cenário, torna-se necessário fortalecer os instrumentos de proteção existentes e criar incentivos econômicos para a conservação. O pagamento por serviços ambientais, que remunera proprietários rurais pela manutenção de vegetação nativa, representa uma alternativa promissora para conciliar produção agropecuária e conservação ambiental.

A sociedade civil também tem papel fundamental nesse processo, tanto por meio da pressão sobre o poder público quanto pela adoção de padrões de consumo mais responsáveis. Escolher produtos com certificação de origem sustentável é uma forma concreta de influenciar as práticas produtivas e contribuir para a conservação do Cerrado.
"""

# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------

DADOS = [
    {
        "nome": "Ana Souza",
        "matricula": "2024001",
        "caso": "limpo",
        "baselines": [
            ("Redação sobre a água", ANA_BASELINE_1),
            ("Redação sobre o desmatamento", ANA_BASELINE_2),
            ("Redação sobre reciclagem", ANA_BASELINE_3),
        ],
        "trabalho_novo": ("Redação sobre aquecimento global", ANA_TRABALHO_NOVO),
    },
    {
        "nome": "Bruno Lima",
        "matricula": "2024002",
        "caso": "ia_detectada",
        "baselines": [
            ("Redação sobre poluição", BRUNO_BASELINE_1),
            ("Redação sobre energia solar", BRUNO_BASELINE_2),
            ("Redação sobre animais em extinção", BRUNO_BASELINE_3),
        ],
        "trabalho_novo": ("Redação sobre preservação ambiental", BRUNO_TRABALHO_IA),
    },
    {
        "nome": "Carla Mendes",
        "matricula": "2024003",
        "caso": "evolucao_legitima",
        "baselines": [
            ("Redação sobre os oceanos", CARLA_BASELINE_1),
            ("Redação sobre poluição marinha", CARLA_BASELINE_2),
            ("Redação sobre degradação dos oceanos", CARLA_BASELINE_3),
        ],
        "trabalho_novo": ("Redação sobre o Cerrado", CARLA_TRABALHO_NOVO),
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Busca ou cria turma
        result = await db.execute(select(Turma).where(Turma.nome == "8º Ano A"))
        turma = result.scalar_one_or_none()
        if not turma:
            turma = Turma(nome="8º Ano A", disciplina="Língua Portuguesa", ano_serie="8º Ano")
            db.add(turma)
            await db.flush()
            print("✓ Turma criada")
        else:
            print("— Turma já existe, usando a existente")

        for dados in DADOS:
            # Busca ou cria aluno
            result = await db.execute(
                select(Aluno).where(Aluno.matricula == dados["matricula"])
            )
            aluno = result.scalar_one_or_none()
            if not aluno:
                aluno = Aluno(nome=dados["nome"], matricula=dados["matricula"], turma_id=turma.id)
                db.add(aluno)
                await db.flush()

            # Remove trabalhos anteriores para recriar limpo
            result = await db.execute(select(Trabalho).where(Trabalho.aluno_id == aluno.id))
            for t in result.scalars().all():
                feat_result = await db.execute(
                    select(TrabalhoFeature).where(TrabalhoFeature.trabalho_id == t.id)
                )
                for f in feat_result.scalars().all():
                    await db.delete(f)
                await db.delete(t)
            await db.flush()

            # Cria baselines
            for titulo, texto in dados["baselines"]:
                t = Trabalho(
                    aluno_id=aluno.id,
                    titulo=titulo,
                    tipo="redação",
                    texto=texto,
                    formato_origem="txt",
                    baseline=True,
                )
                db.add(t)
                await db.flush()
                features = extrair_features(texto)
                for nome, valor in features.items():
                    db.add(TrabalhoFeature(trabalho_id=t.id, nome=nome, valor=valor))

            # Cria trabalho novo (não-baseline)
            titulo, texto = dados["trabalho_novo"]
            t = Trabalho(
                aluno_id=aluno.id,
                titulo=titulo,
                tipo="redação",
                texto=texto,
                formato_origem="txt",
                baseline=False,
            )
            db.add(t)
            await db.flush()
            features = extrair_features(texto)
            for nome, valor in features.items():
                db.add(TrabalhoFeature(trabalho_id=t.id, nome=nome, valor=valor))

            await db.commit()

            # Recalcula perfil
            from app.services.perfil import recalcular_perfil
            await recalcular_perfil(aluno.id, db)

            print(f"✓ {aluno.nome} ({dados['caso']}) — 3 baselines + 1 trabalho novo")

    print("\nPronto! Acesse http://localhost:3000 e vá para a turma '8º Ano A'.")
    print("Abra qualquer trabalho novo e clique em 'Analisar trabalho'.")


if __name__ == "__main__":
    asyncio.run(seed())
