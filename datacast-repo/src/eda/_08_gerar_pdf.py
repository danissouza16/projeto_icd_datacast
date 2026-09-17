# -*- coding: utf-8 -*-
"""Gera o PDF das Secoes 3.2 e 3.4 - Relatorio Sprint 1, Grupo D / DataCast."""
import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Image, Table, TableStyle, PageBreak, KeepTogether, CondPageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIG = os.path.join(BASE, "outputs", "figuras")
SAIDA = os.path.join(BASE, "outputs", "Relatorio_Secoes_3_2_e_3_4_DataCast.pdf")

L = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("Serif", L + "LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B", L + "LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-I", L + "LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Sans", L + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Sans-B", L + "LiberationSans-Bold.ttf"))

AZUL = colors.HexColor("#1f4e79"); VERM = colors.HexColor("#c0392b")
CINZA = colors.HexColor("#555555"); CLARO = colors.HexColor("#f2f5f8")
BORDA = colors.HexColor("#c8d2dc")

S = {
 "titulo":   ParagraphStyle("t", fontName="Sans-B", fontSize=21, leading=26, textColor=AZUL, alignment=TA_CENTER, spaceAfter=6),
 "sub":      ParagraphStyle("s", fontName="Sans", fontSize=12.5, leading=16, textColor=CINZA, alignment=TA_CENTER, spaceAfter=3),
 "h1":       ParagraphStyle("h1", fontName="Sans-B", fontSize=15.5, leading=19, textColor=AZUL, spaceBefore=14, spaceAfter=9),
 "h2":       ParagraphStyle("h2", fontName="Sans-B", fontSize=12.5, leading=16, textColor=colors.HexColor("#2c5f8a"), spaceBefore=12, spaceAfter=6),
 "h3":       ParagraphStyle("h3", fontName="Sans-B", fontSize=11, leading=14, textColor=colors.HexColor("#333333"), spaceBefore=9, spaceAfter=4),
 "p":        ParagraphStyle("p", fontName="Serif", fontSize=10.7, leading=15.4, alignment=TA_JUSTIFY, spaceAfter=7, firstLineIndent=0),
 "li":       ParagraphStyle("li", fontName="Serif", fontSize=10.5, leading=14.6, alignment=TA_JUSTIFY, leftIndent=14, bulletIndent=4, spaceAfter=4),
 "cap":      ParagraphStyle("cap", fontName="Sans", fontSize=8.8, leading=11.6, textColor=CINZA, alignment=TA_CENTER, spaceBefore=4, spaceAfter=11),
 "tab":      ParagraphStyle("tab", fontName="Serif", fontSize=8.6, leading=10.8),
 "tabb":     ParagraphStyle("tabb", fontName="Sans-B", fontSize=8.6, leading=10.8, textColor=colors.white),
 "destaque": ParagraphStyle("d", fontName="Serif", fontSize=10.4, leading=14.6, alignment=TA_JUSTIFY, leftIndent=9, rightIndent=9, spaceBefore=3, spaceAfter=3),
 "dtit":     ParagraphStyle("dt", fontName="Sans-B", fontSize=10, leading=13, textColor=VERM, leftIndent=9, spaceBefore=4, spaceAfter=3),
}

def P(t, st="p"): return Paragraph(t, S[st])
def B(t): return Paragraph(t, S["li"], bulletText="•")

def fig(nome, legenda, larg=16.4):
    """Insere figura ajustada a largura util, com legenda."""
    cam = os.path.join(FIG, nome)
    w, h = PILImage.open(cam).size
    lw = larg * cm; lh = lw * h / w
    maxh = 20.4 * cm
    if lh > maxh: lh = maxh; lw = lh * w / h
    return KeepTogether([Image(cam, width=lw, height=lh), P(legenda, "cap")])

def caixa(titulo, linhas, cor=VERM):
    itens = [Paragraph(titulo, ParagraphStyle("x", parent=S["dtit"], textColor=cor))]
    itens += [P(l, "destaque") for l in linhas]
    t = Table([[itens]], colWidths=[16.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CLARO),
        ("BOX", (0,0), (-1,-1), 0.9, cor),
        ("LINEBEFORE", (0,0), (0,-1), 3.2, cor),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 8)]))
    return KeepTogether([Spacer(1, 5), t, Spacer(1, 9)])

def tabela(cab, linhas, larguras, alin=None):
    dados = [[Paragraph(c, S["tabb"]) for c in cab]]
    dados += [[Paragraph(str(c), S["tab"]) for c in l] for l in linhas]
    t = Table(dados, colWidths=[w * cm for w in larguras], repeatRows=1)
    est = [("BACKGROUND", (0,0), (-1,0), AZUL),
           ("GRID", (0,0), (-1,-1), 0.4, BORDA),
           ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
           ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
           ("TOPPADDING", (0,0), (-1,-1), 3.5), ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
           ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CLARO])]
    for c in (alin or []): est.append(("ALIGN", (c,1), (c,-1), "CENTER"))
    t.setStyle(TableStyle(est))
    return t

def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sans", 7.8); canvas.setFillColor(CINZA)
    canvas.drawString(2.3*cm, 1.25*cm, "DataCast — Grupo D | ENG 4040 — Projeto Integrado 4 | Relatório Sprint 1")
    canvas.drawRightString(A4[0]-2.3*cm, 1.25*cm, f"{doc.page}")
    canvas.setStrokeColor(BORDA); canvas.setLineWidth(0.5)
    canvas.line(2.3*cm, 1.62*cm, A4[0]-2.3*cm, 1.62*cm)
    canvas.restoreState()

doc = BaseDocTemplate(SAIDA, pagesize=A4, leftMargin=2.3*cm, rightMargin=2.3*cm,
                      topMargin=2.0*cm, bottomMargin=2.1*cm,
                      title="Seções 3.2 e 3.4 — Análise Exploratória | DataCast",
                      author="Grupo D — DataCast")
doc.addPageTemplates([PageTemplate(id="n",
    frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=rodape)])

E = []

# ==================================================================== #
# CAPA
# ==================================================================== #
E += [Spacer(1, 1.7*cm),
      P("Análise Exploratória de Dados", "titulo"),
      P("Seções 3.2 e 3.4", "titulo"),
      Spacer(1, 0.5*cm),
      P("Projeto DataCast — Previsão de Risco de Enchentes na Região Sudeste", "sub"),
      P("ENG 4040 — Projeto Integrado 4 | Grupo D", "sub"),
      P("Cliente: Ministério do Meio Ambiente e Mudança do Clima", "sub"),
      Spacer(1, 0.9*cm)]

E += [tabela(["Integrante", "Matrícula"],
             [["Rodrigo Touma Costa", "2510583"], ["Raphael Vincenzo Maniero", "2510285"],
              ["Eduardo Luiz Meireles", "2510502"], ["Pedro Monteiro Bernardes", "2510962"],
              ["Daniel Santana", "2310995"]], [9.2, 4.0], alin=[1]),
      Spacer(1, 0.8*cm)]

E += [P("Base analisada", "h2"),
      tabela(["Característica", "Valor"],
             [["Arquivo", "<font name='Sans'>dataset_limpo_final.csv</font>"],
              ["Registros", "7.458.432 observações horárias"],
              ["Variáveis", "26 colunas (20 numéricas, 2 categóricas, 2 booleanas, data e hora)"],
              ["Período", "01/01/2019 a 31/12/2024 (6 anos completos)"],
              ["Cobertura", "146 municípios — MG (68), SP (42), RJ (23), ES (13)"],
              ["Fontes", "INMET (meteorologia horária), CEMADEN (chuva), ANA/HidroWeb (cota e vazão)"]],
             [3.8, 12.6]),
      Spacer(1, 0.7*cm)]

E += [caixa("Como este documento foi produzido", [
    "Todos os números, tabelas e figuras deste relatório foram gerados pela execução dos scripts em "
    "<font name='Sans'>src/eda/</font> sobre a base completa de 7,4 milhões de registros — nenhum valor foi "
    "estimado ou transcrito de execuções anteriores. Os scripts são determinísticos "
    "(<font name='Sans'>random_state=42</font>), e as tabelas de apoio estão em "
    "<font name='Sans'>outputs/tabelas/</font>.",
], cor=AZUL), PageBreak()]

# ==================================================================== #
# SUMARIO EXECUTIVO
# ==================================================================== #
E += [P("Sumário dos achados", "h1"),
      P("A análise exploratória da base integrada produziu cinco conclusões que orientam diretamente a "
        "modelagem prevista para as próximas sprints. Duas delas são achados de qualidade de dados que "
        "exigem correção no pipeline antes do treinamento de qualquer modelo.", "p")]

E += [tabela(["#", "Achado", "Evidência", "Consequência"],
    [["1", "A chuva do CEMADEN está somada entre estações, não mediada",
      "Correlação de +0,910 entre o nº de estações do município e a chuva média registrada",
      "Variável inutilizável como está; exige recálculo por média"],
     ["2", "A pressão atmosférica bruta mede altitude, não tempo",
      "99,1% da variância é explicada pelo município (R²=0,991)",
      "Usar anomalia em relação à média da estação"],
     ["3", "Chuva e vazão não se correlacionam na mesma hora",
      "ρ = +0,04 na hora; ρ = +0,61 com acumulado de 60 dias",
      "O preditor é a chuva acumulada, não a instantânea"],
     ["4", "Doze pares de variáveis são redundantes (|r| ≥ 0,95)",
      "O trio de pressão tem r = 1,000 entre si",
      "Reduzir de 20 para ~10 variáveis independentes"],
     ["5", "Os eventos de interesse são raros",
      "Dias acima do p99 local de vazão: 1,01% (proporção 1:98)",
      "Exige reamostragem ou ponderação de classes"]],
    [0.8, 4.2, 5.2, 4.6]),
      Spacer(1, 0.5*cm)]

E += [PageBreak()]

# ==================================================================== #
# SECAO 3.2
# ==================================================================== #
E += [P("3.2 Distribuição das variáveis", "h1")]

E += [P("Esta seção examina a forma da distribuição de cada uma das 20 variáveis numéricas da base. "
        "O objetivo não é apenas descrever, mas identificar quais variáveis violam as premissas de "
        "simetria e homogeneidade que a maioria dos algoritmos assume, e quais apresentam comportamento "
        "que decorre da construção da base e não do fenômeno físico observado.", "p")]

E += [fig("3_2_painel_histogramas.png",
          "Figura 1 — Distribuição das 20 variáveis numéricas. As variáveis com assimetria superior a 3 "
          "em módulo (precipitação, chuva CEMADEN e vazão) estão em escala logarítmica no eixo vertical, "
          "sem a qual a barra do zero suprimiria visualmente todo o restante da distribuição.")]

E += [P("A leitura do painel revela que as variáveis se organizam em quatro comportamentos distintos, "
        "tratados a seguir.", "p")]

# ---- 3.2.1 chuva ----
E += [P("3.2.1 Precipitação: assimetria extrema e massa concentrada no zero", "h2")]

E += [P("A precipitação é a variável mais problemática da base do ponto de vista estatístico, e também "
        "a mais importante para o projeto. Dos 6.324.455 registros horários válidos do INMET, "
        "<b>92,58% são exatamente zero</b> — não chove na esmagadora maioria das horas. O coeficiente de "
        "assimetria é de 18,99 e a curtose de 568,22, valores que caracterizam uma distribuição "
        "radicalmente afastada da normalidade.", "p")]

E += [fig("3_2_precipitacao_detalhe.png",
          "Figura 2 — Precipitação em duas leituras. À esquerda, todas as horas em escala logarítmica: a "
          "barra do zero é três ordens de grandeza maior que a barra seguinte. À direita, apenas as horas "
          "com chuva registrada, em escala log-log, onde a distribuição se revela aproximadamente "
          "exponencial. O padrão de \"pente\" nos valores baixos reflete a resolução de 0,2 mm do "
          "pluviômetro de báscula.")]

E += [P("Ao isolar apenas as horas em que houve chuva (Figura 2, painéis à direita), a distribuição "
        "deixa de ser degenerada e assume forma aproximadamente exponencial. Os percentis condicionais "
        "quantificam a cauda:", "p")]

E += [tabela(["Fonte", "Horas com chuva", "Mediana (>0)", "p90 (>0)", "p99 (>0)", "Máximo", "% das horas > 25 mm"],
    [["INMET", "469.530", "0,6 mm", "5,0 mm", "21,0 mm", "131,0 mm", "0,047%"],
     ["CEMADEN", "654.920", "0,8 mm", "9,1 mm", "71,6 mm", "399,4 mm", "0,603%"]],
    [2.4, 2.7, 2.4, 2.1, 2.1, 2.1, 2.6], alin=[1,2,3,4,5,6]),
      P("Tabela 1 — Distribuição condicional da precipitação, considerando apenas as horas com registro "
        "positivo. Os valores do CEMADEN são sistematicamente maiores; a Seção 3.4.4 demonstra que isso "
        "é um artefato de agregação, não um fenômeno meteorológico.", "cap")]

E += [P("A consequência prática é direta. Uma métrica de erro médio, como o RMSE, será dominada pelos "
        "92,58% de horas secas, e um modelo que sempre preveja \"não chove\" alcançaria acurácia "
        "aparentemente excelente sem qualquer utilidade operacional. O problema que o cliente precisa "
        "resolver — antecipar eventos de enchente — está inteiramente contido na cauda direita, que "
        "representa menos de 0,05% das observações.", "p")]

E += [caixa("Implicação para a modelagem", [
    "A precipitação não deve ser modelada como variável contínua única. Recomenda-se decompô-la em "
    "(i) um componente binário de ocorrência (chove / não chove) e (ii) um componente de intensidade "
    "condicional à ocorrência, ou aplicar transformação logarítmica do tipo <font name='Sans'>log(1+x)</font> "
    "antes de qualquer método sensível à escala. A avaliação deve usar métricas orientadas à cauda "
    "(recall dos eventos extremos, área sob a curva precisão-recall), nunca acurácia global."])]

# ---- 3.2.2 hidrologicas ----
E += [P("3.2.2 Variáveis hidrológicas: lognormalidade e cota negativa", "h2")]

E += [fig("3_2_hidrologicas.png",
          "Figura 3 — Cota e vazão. A cota (esquerda) é aproximadamente simétrica em torno de 123 cm, com "
          "0,91% de leituras negativas. A vazão em escala linear (centro) parece degenerada; em escala "
          "logarítmica (direita) revela-se aproximadamente lognormal.")]

E += [P("A vazão apresenta assimetria de 7,91 e curtose de 97,32: a mediana é de apenas 13,5 m³/s, "
        "enquanto o percentil 99 chega a 1.408,9 m³/s e o máximo a 6.805,9 m³/s — uma razão de mais de "
        "500 vezes entre a mediana e o extremo. Contudo, o painel direito da Figura 3 mostra que essa "
        "assimetria desaparece sob transformação logarítmica, o que indica distribuição aproximadamente "
        "lognormal. Isso é uma boa notícia: diferentemente da precipitação, cuja massa em zero é "
        "irredutível, a vazão pode ser normalizada por uma transformação simples.", "p")]

E += [P("Um ponto que merece registro é a existência de <b>0,91% de valores negativos de cota</b>, com "
        "mínimo de −145 cm. Não se trata de erro: a cota é medida em relação ao zero da régua "
        "linimétrica instalada na estação, referência arbitrária que pode estar acima do leito em "
        "períodos de estiagem severa. Esses valores foram corretamente preservados pela etapa de "
        "limpeza, que filtrou apenas faixas fisicamente implausíveis.", "p")]

# ---- 3.2.3 meteorologicas ----
E += [P("3.2.3 Variáveis meteorológicas contínuas", "h2")]

E += [fig("3_2_meteorologicas.png",
          "Figura 4 — Seis variáveis meteorológicas com médias e medianas assinaladas. A proximidade "
          "entre as duas medidas indica simetria; o afastamento, assimetria.")]

E += [P("Temperatura do ar e umidade relativa comportam-se de forma próxima ao esperado. A temperatura "
        "é quase simétrica (assimetria −0,08), centrada em 22,3 °C, com amplitude de −9,0 °C a 42,9 °C "
        "compatível com a diversidade altimétrica do Sudeste. A umidade relativa é assimétrica à "
        "esquerda (−0,61) e acumula massa próximo de 100%, situação normal em noites de "
        "saturação do ar.", "p")]

E += [P("A radiação global merece leitura cuidadosa: 2,80% de valores exatamente zero e mediana de "
        "159,8 KJ/m² contra média de 787,8 KJ/m². A explicação não é estatística, mas física — a base "
        "é horária e inclui as horas noturnas, quando a radiação é legitimamente nula. A distribuição "
        "bimodal aparente é o ciclo dia-noite, e não uma anomalia. O teto de 4.000 KJ/m² imposto pela "
        "limpeza afeta apenas 0,0013% dos registros.", "p")]

E += [P("A direção do vento, por sua vez, é a única variável genuinamente circular da base: 1° e 360° "
        "são fisicamente idênticos, mas numericamente distantes. Tratá-la como variável linear "
        "introduziria erro sistemático; a decomposição em componentes seno e cosseno é o tratamento "
        "adequado.", "p")]

# ---- 3.2.4 pressao ----
E += [P("3.2.4 Pressão atmosférica: uma distribuição que mede altitude", "h2")]

E += [P("O painel da pressão na Figura 1 exibe um perfil claramente multimodal, com concentrações em "
        "torno de 910, 950 e 1.012 mB. Distribuições multimodais normalmente indicam mistura de "
        "subpopulações, e a investigação confirmou a hipótese de forma inequívoca.", "p")]

E += [caixa("Achado — a pressão bruta é um identificador geográfico disfarçado", [
    "O município de origem explica <b>99,1% da variância</b> da pressão atmosférica (R² = 0,991). "
    "O desvio-padrão <i>entre</i> municípios é de 36,9 mB, enquanto o desvio-padrão <i>dentro</i> de "
    "cada município é de apenas 3,4 mB — uma razão de quase onze vezes.",
    "Os extremos ilustram o mecanismo: Diamantina (MG), a cerca de 1.300 m de altitude, registra média "
    "de 868,4 mB, enquanto Vitória (ES), ao nível do mar, registra 1.015,8 mB. A diferença de 147 mB "
    "entre os dois é altimétrica, não meteorológica.",
    "<b>Consequência:</b> alimentar um modelo com a pressão bruta equivale a fornecer a altitude da "
    "estação. O modelo aprenderá a identificar o local, não a antecipar o tempo. A variável deve ser "
    "convertida em anomalia — o desvio em relação à média histórica da própria estação — que é onde "
    "reside o sinal meteorológico (as quedas de pressão que antecedem sistemas frontais)."])]

# ---- 3.2.5 completude ----
E += [P("3.2.5 Completude das variáveis", "h2")]

E += [fig("3_2_completude.png",
          "Figura 5 — Percentual de valores ausentes por variável após a limpeza. Verde: abaixo de 12%; "
          "laranja: entre 12% e 40%; vermelho: acima de 40%.", larg=13.6)]

E += [P("As variáveis do INMET apresentam ausência entre 7,6% e 15,2%, resultado já favorável da "
        "interpolação linear com limite de seis horas aplicada na etapa de limpeza. A precipitação "
        "destoa do bloco meteorológico com 15,2% de ausência justamente porque foi deliberadamente "
        "excluída da interpolação — interpolar chuva criaria precipitação onde não houve, contaminando "
        "a variável central do projeto com dados sintéticos.", "p")]

E += [P("Os três maiores percentuais têm origem distinta e não representam falha de sensor. A chuva do "
        "CEMADEN está ausente em 46,63% dos registros e as variáveis da ANA em cerca de 69% porque nem "
        "todo município do recorte possui estação dessas redes. Trata-se de <b>limitação de cobertura "
        "geográfica</b>, informação que as colunas <font name='Sans'>tem_estacao_cemaden</font> e "
        "<font name='Sans'>tem_estacao_ana</font> registram explicitamente. A Figura 14, na Seção 3.4.6, "
        "mapeia essa cobertura.", "p")]

E += [PageBreak()]

# ==================================================================== #
# SECAO 3.4
# ==================================================================== #
E += [P("3.4 Análise de relações entre variáveis", "h1")]

E += [P("Esta seção investiga como as variáveis se relacionam entre si, com atenção particular à "
        "relação entre precipitação e vazão — o par que sustenta a hipótese central do projeto. "
        "A análise combina correlação linear (Pearson) e monotônica (Spearman), gráficos de dispersão, "
        "séries temporais e distribuição espacial.", "p")]

# ---- 3.4.1 correlacao ----
E += [P("3.4.1 Matriz de correlação: estrutura em blocos", "h2")]

E += [fig("3_4_heatmap_correlacao.png",
          "Figura 6 — Matriz de correlação de Pearson entre as 20 variáveis numéricas, calculada sobre a "
          "base completa. Apenas o triângulo inferior é exibido, por simetria. Os blocos vermelhos "
          "contíguos na diagonal são grupos de variáveis mutuamente redundantes.", larg=15.2)]

E += [P("A matriz não se distribui uniformemente: ela se organiza em <b>blocos</b>. Doze pares de "
        "variáveis apresentam correlação absoluta igual ou superior a 0,95, e três pares superam 0,99. "
        "Esses blocos correspondem a grupos em que a mesma grandeza física foi registrada em três "
        "colunas distintas — o valor instantâneo, o máximo da hora anterior e o mínimo da hora "
        "anterior.", "p")]

E += [tabela(["Bloco redundante", "Colunas", "Faixa de correlação interna"],
    [["Pressão atmosférica", "3", "r = 1,000 (indistinguíveis em duas casas decimais)"],
     ["Temperatura do ar", "3", "r entre 0,982 e 0,988"],
     ["Temperatura do ponto de orvalho", "3", "r entre 0,977 e 0,988"],
     ["Umidade relativa", "3", "r entre 0,969 e 0,980"],
     ["Vento (velocidade e rajada)", "2", "r = 0,844"]],
    [5.2, 1.8, 9.4], alin=[1]),
      P("Tabela 2 — Blocos de variáveis redundantes identificados pela matriz de correlação.", "cap")]

E += [fig("3_4_top_correlacoes.png",
          "Figura 7 — Os dezoito pares de maior correlação absoluta. Em vermelho, os pares redundantes "
          "(|r| ≥ 0,95); em azul, os pares que carregam informação genuinamente distinta.", larg=13.4)]

E += [P("O caso da pressão é o mais extremo: as três colunas são estatisticamente indistinguíveis, o que "
        "faz sentido físico, já que a pressão varia lentamente e a diferença entre o valor instantâneo e "
        "os extremos da hora anterior é desprezível frente à sua amplitude total. Manter as três colunas "
        "em um modelo introduz multicolinearidade severa, que desestabiliza coeficientes em métodos "
        "lineares e distorce medidas de importância de variáveis em métodos baseados em árvores.", "p")]

E += [caixa("Implicação para a modelagem", [
    "O conjunto de 20 variáveis numéricas carrega, na prática, cerca de 10 dimensões independentes. "
    "Recomenda-se manter uma coluna representativa por bloco (preferencialmente o valor instantâneo, "
    "que é o disponível em tempo real numa aplicação operacional) e descartar as demais, ou derivar a "
    "amplitude horária (máximo menos mínimo) como variável nova — esta sim informativa, pois mede a "
    "instabilidade atmosférica dentro da hora."], cor=AZUL)]

E += [P("Fora dos blocos redundantes, a relação mais forte é a <b>anticorrelação entre temperatura e "
        "umidade relativa (r = −0,650)</b>. É a única correlação alta da base que não decorre de "
        "duplicação de coluna: ela reflete o mecanismo físico pelo qual o aquecimento do ar aumenta sua "
        "capacidade de retenção de vapor, reduzindo a umidade relativa sem alteração da umidade "
        "absoluta.", "p")]

# ---- 3.4.2 dispersao ----
E += [P("3.4.2 Gráficos de dispersão", "h2")]

E += [fig("3_4_dispersao.png",
          "Figura 8 — Quatro pares de variáveis em dispersão. (a) temperatura × umidade em mapa de "
          "densidade hexagonal; (b) concordância entre as duas fontes de chuva; (c) chuva e vazão na "
          "mesma hora; (d) cota × vazão, com seis municípios destacados sobre o conjunto em cinza.")]

E += [P("<b>Painel (a) — Temperatura × Umidade.</b> A nuvem tem orientação descendente clara e formato "
        "de banda, não de elipse: a dispersão da umidade é muito maior nas temperaturas baixas "
        "(variando de 20% a 100%) do que nas altas. A relação, portanto, é forte mas não estritamente "
        "linear, e a proximidade entre Pearson (−0,647) e Spearman (−0,639) confirma que é ao menos "
        "consistentemente monotônica. O acúmulo na faixa de 100% de umidade é o teto físico do "
        "instrumento.", "p")]

E += [P("<b>Painel (b) — INMET × CEMADEN.</b> As duas fontes medem a mesma grandeza em locais próximos, "
        "e a expectativa razoável seria que os pontos se alinhassem à reta de identidade. Não é o que se "
        "observa: a correlação de Pearson é de apenas 0,278 e a nuvem está sistematicamente deslocada "
        "para cima da diagonal, indicando que o CEMADEN registra valores muito superiores. A concordância "
        "binária — se houve ou não chuva — é de 86,5%, bem melhor que a concordância de intensidade. "
        "A Seção 3.4.4 identifica a causa.", "p")]

E += [P("<b>Painel (c) — Chuva × Vazão.</b> Este é o resultado mais contraintuitivo da análise. O par de "
        "variáveis que define o problema do projeto apresenta correlação praticamente nula na escala "
        "horária: Pearson de −0,014 e Spearman de +0,035. A nuvem de pontos é uma faixa vertical junto "
        "ao eixo — para qualquer valor de chuva, observa-se todo o espectro de vazões. A Seção 3.4.3 "
        "demonstra que a ausência de correlação é aparente e decorre da escala temporal escolhida.", "p")]

E += [P("<b>Painel (d) — Cota × Vazão.</b> Globalmente a correlação é moderada (r = +0,426 na amostra), "
        "o que surpreende, já que vazão é calculada a partir da cota por meio da curva-chave da estação. "
        "Ao colorir seis municípios individualmente, a explicação torna-se visível: cada município traça "
        "sua <b>própria curva</b>, nítida e monotônica, mas deslocada das demais. Uma cota de 200 cm "
        "corresponde a 1 m³/s num rio e a 300 m³/s em outro, pois a relação depende da geometria "
        "da seção do rio.", "p")]

E += [caixa("Achado — a agregação entre municípios destrói relações reais", [
    "A correlação entre cota e vazão é de <b>+0,437 quando todos os municípios são analisados juntos</b>, "
    "mas de <b>+0,957 (mediana) quando calculada dentro de cada município</b> separadamente, sobre "
    "52 municípios com dados suficientes. O intervalo interquartil intramunicipal vai de +0,932 a +0,981.",
    "Trata-se de uma manifestação do paradoxo de Simpson: misturar populações com relações internas "
    "fortes mas de níveis distintos produz uma correlação agregada artificialmente fraca.",
    "<b>Consequência:</b> toda estatística desta base deve ser interpretada — e todo modelo deve ser "
    "treinado — condicionando ao município ou ao rio. Um modelo global sobre dados agrupados "
    "subestimará sistematicamente a força das relações hidrológicas."])]

# ---- 3.4.3 defasagem ----
E += [P("3.4.3 Defasagem e acumulação: por que a correlação horária é nula", "h2")]

E += [P("A correlação nula entre chuva e vazão observada no painel (c) da Figura 8 exigia investigação, "
        "por contrariar tanto a hipótese do projeto quanto a hidrologia elementar. Duas hipóteses foram "
        "testadas: que a vazão responde à chuva com atraso, e que responde ao volume acumulado em vez da "
        "intensidade instantânea. Ambas se confirmaram.", "p")]

E += [P("Para isolar o efeito identificado na seção anterior, as correlações foram calculadas <b>dentro "
        "de cada município</b> e agregadas pela mediana, sobre séries diárias de 52 municípios com "
        "estação fluviométrica (111.792 pares município-dia).", "p")]

E += [fig("3_4_defasagem.png",
          "Figura 9 — (a) Correlação de Spearman entre chuva e vazão conforme a defasagem aplicada à "
          "chuva. (b) Correlação entre chuva acumulada em janelas crescentes e vazão do dia; a faixa "
          "sombreada é o intervalo interquartil entre municípios.")]

E += [P("O painel (a) mostra que a correlação parte de ρ = 0,286 sem defasagem, <b>atinge o máximo de "
        "ρ = 0,343 com três dias de atraso</b> e decai lentamente a partir daí. A existência de um pico "
        "bem definido é a assinatura do tempo de concentração da bacia: a água precipitada leva dias "
        "para escoar pela superfície, infiltrar e alcançar a seção do rio onde a estação mede.", "p")]

E += [P("O painel (b) é ainda mais decisivo. Acumulando a chuva em janelas progressivamente maiores, a "
        "correlação cresce de forma monotônica:", "p")]

E += [tabela(["Janela de acumulação", "1 dia", "3 dias", "7 dias", "15 dias", "30 dias", "60 dias"],
    [["Spearman ρ (mediana intramunicipal)", "0,286", "0,396", "0,479", "0,508", "0,513", "0,607"]],
    [5.6, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8], alin=[1,2,3,4,5,6]),
      P("Tabela 3 — Correlação entre chuva acumulada e vazão do dia. O sinal mais que dobra ao passar da "
        "chuva de um dia para o acumulado de dois meses.", "cap")]

E += [caixa("Achado — o preditor de vazão é o acumulado, não a chuva instantânea", [
    "A correlação entre chuva e vazão passa de <b>ρ ≈ 0,04 na escala horária</b> para <b>ρ = 0,61 com "
    "acumulado de 60 dias</b>, um ganho de mais de quinze vezes obtido apenas pela reformulação da "
    "variável, sem qualquer dado novo.",
    "A interpretação hidrológica é direta: a vazão de um rio reflete o estado de saturação da bacia, "
    "construído ao longo de semanas, e não a chuva da hora corrente. Uma chuva intensa sobre solo seco "
    "infiltra; a mesma chuva sobre solo saturado escoa integralmente e produz a cheia.",
    "<b>Consequência:</b> o conjunto de variáveis preditoras deve incluir somas móveis de precipitação "
    "em janelas de 3, 7, 15, 30 e 60 dias, além de versões defasadas em 1 a 3 dias. Esta é a etapa de "
    "engenharia de variáveis de maior retorno esperado para a próxima sprint."])]

# ---- 3.4.4 cemaden ----
E += [P("3.4.4 Achado de integração na variável de chuva do CEMADEN", "h2")]

E += [P("A discrepância entre INMET e CEMADEN observada no painel (b) da Figura 8 mostrou-se sistemática "
        "e quantificável. O volume total de chuva registrado pelo CEMADEN no período é <b>4,65 vezes</b> "
        "o registrado pelo INMET nos mesmos município-horas, e o valor máximo da série chega a "
        "399,4 mm em uma única hora — próximo do recorde mundial de precipitação horária, o que é "
        "implausível para 694 ocorrências distribuídas em 20 municípios.", "p")]

E += [P("A distribuição geográfica dessas ocorrências deu a pista decisiva: elas concentram-se em São "
        "Paulo (250 registros), Angra dos Reis (182), Rio de Janeiro (77) e Juiz de Fora (70) — "
        "precisamente os municípios com as redes de monitoramento mais densas. Testou-se então a "
        "hipótese de que a agregação horária somou as leituras de todas as estações do município, em vez "
        "de calcular sua média.", "p")]

E += [fig("3_4_achado_cemaden.png",
          "Figura 10 — (a) Chuva horária média registrada contra o número de estações CEMADEN do "
          "município, com o INMET como referência. (b) Comparação agregada por faixa de densidade de "
          "estações.")]

E += [caixa("Achado — chuva_cemaden_mm é a soma entre estações, não a média", [
    "A correlação entre o número de estações CEMADEN de um município e a chuva horária média ali "
    "registrada é de <b>r = +0,910</b> (Spearman ρ = +0,926), sobre 86 municípios. A precipitação é um "
    "fenômeno físico: a quantidade de chuva que cai não pode depender de quantos pluviômetros a medem.",
    "A verificação pelo INMET confirma o diagnóstico. Municípios com uma única estação CEMADEN "
    "registram média de 0,12 mm/h; os com mais de dez estações registram 2,83 mm/h — uma inflação de "
    "<b>23 vezes</b>. No mesmo recorte de municípios, a média do INMET permanece estável entre 0,14 e "
    "0,20 mm/h, como esperado de um sensor único por município.",
    "O caso extremo é São Paulo: com 82 estações, a base atribui ao município chuva horária média de "
    "7,39 mm/h, equivalente a cerca de 64.700 mm anuais — aproximadamente quarenta vezes a "
    "precipitação real da cidade.",
    "<b>Consequência:</b> a variável <font name='Sans'>chuva_cemaden_mm</font> não pode ser utilizada em "
    "sua forma atual, e qualquer modelo treinado com ela aprenderá a densidade da rede de sensores "
    "como se fosse intensidade de chuva. A correção exige refazer a agregação do CEMADEN substituindo "
    "a soma entre estações por média (ou máximo, se o objetivo for captar o núcleo mais intenso da "
    "célula de chuva), preservando a soma apenas entre as leituras de dez minutos de uma mesma "
    "estação dentro da hora."])]

E += [P("Registre-se que este achado não invalida a etapa de integração como um todo: o cruzamento de "
        "chaves, a normalização de nomes de municípios e o alinhamento temporal funcionaram "
        "corretamente, como atesta a concordância binária de 86,5% entre as duas fontes quanto à "
        "ocorrência de chuva. O problema está circunscrito à função de agregação aplicada na etapa "
        "de consolidação.", "p")]



# ---- 3.4.5 series temporais ----
E += [P("3.4.5 Séries temporais", "h2")]

E += [P("A análise temporal utiliza cinco municípios sorteados entre os 46 que possuem série de vazão "
        "com mais de 1.200 dias válidos. O sorteio é reprodutível "
        "(<font name='Sans'>random.seed(42)</font>).", "p")]

E += [fig("3_4_series_temporais.png",
          "Figura 11 — Chuva diária acumulada (barras azuis, eixo invertido no topo) e vazão média diária "
          "(linha vermelha) para cinco municípios, 2019–2024. A linha laranja tracejada marca o percentil "
          "99 local de vazão. O eixo da chuva é invertido por convenção hidrológica, para que a chuva "
          "\"caia\" sobre o hidrograma.", larg=15.6)]

E += [P("Três padrões aparecem de forma consistente nos cinco municípios. O primeiro é a <b>sazonalidade "
        "marcada</b>: os picos de vazão concentram-se sistematicamente entre dezembro e março, e os "
        "mínimos entre julho e setembro. O semestre úmido (outubro a março) acumula 1.089 mm de "
        "precipitação média contra 229 mm do semestre seco — uma razão de <b>4,8 vezes</b>.", "p")]

E += [P("O segundo padrão é a <b>assimetria da forma do hidrograma</b>: a subida da vazão é abrupta, "
        "concentrada em poucos dias, enquanto a recessão é lenta e se estende por semanas. Essa "
        "assimetria é a assinatura da resposta de bacia — escoamento superficial rápido na cheia, "
        "esvaziamento gradual do armazenamento subterrâneo na recessão — e explica por que a correlação "
        "simétrica de Pearson captura mal a relação.", "p")]

E += [P("O terceiro é a <b>variabilidade interanual</b>. Em São Romão, o pico de 2022 supera 6.800 m³/s, "
        "enquanto o de 2021 não alcança 2.000 m³/s. Um modelo treinado apenas em anos secos não "
        "generalizará para os úmidos, o que torna imprescindível que a partição entre treino e "
        "validação preserve anos completos, e não divida aleatoriamente as observações.", "p")]

E += [fig("3_4_evento_extremo.png",
          "Figura 12 — Detalhe do maior evento da base: São Romão (MG), janela de 90 dias em torno do "
          "pico de 20 de janeiro de 2022, correspondente às enchentes que atingiram Minas Gerais naquele "
          "verão.", larg=15.6)]

E += [P("O zoom no maior evento registrado torna visível o mecanismo descrito na Seção 3.4.3. Ao longo "
        "de dezembro de 2021 acumula-se uma sucessão de dias chuvosos, e a vazão sobe de forma "
        "gradual, de cerca de 1.300 m³/s para 3.000 m³/s. O salto final até 6.806 m³/s ocorre em janeiro, "
        "sobre uma bacia já saturada. Nenhum dia isolado de chuva explica o pico; o que o explica é o "
        "acúmulo das seis a oito semanas anteriores — exatamente o horizonte em que a análise de "
        "janelas encontrou o sinal mais forte.", "p")]

E += [P("A base também registra o <b>ciclo diário</b> da precipitação. Os dados estão em UTC, e a chuva "
        "média por hora tem máximo às 21h UTC (18h no horário de Brasília) e mínimo às 13h UTC (10h "
        "local). Trata-se do padrão convectivo clássico do Sudeste — aquecimento diurno da superfície, "
        "convecção e precipitação no fim da tarde. A coerência desse ciclo com a física esperada "
        "funciona como validação independente do alinhamento temporal executado na integração.", "p")]

# ---- 3.4.6 geoespacial ----
E += [P("3.4.6 Distribuição espacial", "h2")]

E += [fig("3_4_geoespacial.png",
          "Figura 13 — Precipitação média anual e vazão média por município. Os municípios foram "
          "geocodificados por cruzamento com a tabela pública de coordenadas do IBGE (143 dos 146 "
          "municípios obtiveram correspondência). Os pontos cinza ao fundo são todos os municípios do "
          "Sudeste, e desenham o contorno da região.", larg=15.6)]

E += [P("O mapa de precipitação reproduz com fidelidade a climatologia conhecida do Sudeste. A faixa de "
        "maior precipitação acompanha a <b>Serra do Mar</b>, no litoral de São Paulo e Rio de Janeiro — "
        "Bertioga, Iguape, Itatiaia e Teresópolis lideram —, onde a orografia força a ascensão do ar "
        "úmido oceânico. O quadrante norte de Minas Gerais apresenta os menores valores, consistente com "
        "sua transição para o semiárido. Esse gradiente noroeste-sudeste é uma validação relevante: "
        "a base reproduz um padrão climatológico independente, que não foi imposto por nenhuma etapa "
        "do processamento.", "p")]

E += [P("O mapa de vazão segue lógica distinta, e a comparação entre os dois é instrutiva. Os maiores "
        "valores não estão onde mais chove, mas onde a <b>área de drenagem acumulada</b> é maior — São "
        "Romão e Pirapora, no médio São Francisco, e Linhares, na foz do rio Doce. A vazão é uma "
        "variável integrada no espaço, enquanto a precipitação é local. Isso reforça que a posição do "
        "município na bacia hidrográfica é uma variável explicativa ausente da base atual e "
        "potencialmente valiosa.", "p")]

E += [fig("3_4_cobertura_fontes.png",
          "Figura 14 — Combinação de fontes disponível em cada município. A ausência de dados "
          "hidrológicos é uma característica geográfica da rede de monitoramento, não uma falha de "
          "medição.", larg=12.4)]

E += [P("O mapa de cobertura explica visualmente os percentuais de ausência discutidos na Seção 3.2.5. "
        "Apenas <b>38 dos 143 municípios</b> geocodificados dispõem das três fontes simultaneamente; "
        "43 contam somente com o INMET. Os municípios com estação da ANA concentram-se ao longo dos "
        "grandes eixos fluviais, o que é coerente com a finalidade da rede fluviométrica nacional.", "p")]

E += [P("Essa distribuição impõe uma restrição de escopo que precisa ser explicitada ao cliente: um "
        "modelo que preveja vazão só pode ser treinado e validado nos 52 municípios com dados "
        "hidrológicos. Estendê-lo aos demais exigiria uma estratégia de regionalização — transferir "
        "parâmetros de bacias monitoradas para bacias sem monitoramento —, o que constitui um problema "
        "metodológico distinto e de dificuldade consideravelmente maior.", "p")]

# ---- 3.4.7 desbalanceamento ----
E += [P("3.4.7 Raridade dos eventos de interesse", "h2")]

E += [P("A última relação relevante é entre o volume de dados e a quantidade de eventos efetivamente "
        "úteis ao objetivo do projeto. Adotando o percentil 99 local da vazão como limiar operacional "
        "de cheia — critério que respeita a escala própria de cada rio, conforme exige o achado da "
        "Seção 3.4.2 —, obtém-se o seguinte quadro:", "p")]

E += [tabela(["Definição de evento", "Ocorrências", "Total", "Frequência", "Proporção"],
    [["Dia acima do p95 local de vazão", "4.846", "97.313 dias-município", "4,98%", "1 : 19"],
     ["Dia acima do p99 local de vazão", "982", "97.313 dias-município", "1,01%", "1 : 98"],
     ["Hora com chuva INMET acima de 25 mm", "2.948", "6.324.455 horas", "0,047%", "1 : 2.145"]],
    [5.4, 2.4, 4.0, 2.2, 2.4], alin=[1,2,3,4]),
      P("Tabela 4 — Frequência dos eventos extremos sob três definições operacionais.", "cap")]

E += [P("De 7,4 milhões de registros horários, restam menos de mil dias-município que caracterizam cheia "
        "sob o critério mais restritivo. O volume bruto da base é enganoso: o que determina a "
        "viabilidade do modelo não é o número total de observações, mas o número de eventos positivos "
        "disponíveis para o aprendizado.", "p")]

E += [caixa("Implicação para a modelagem", [
    "Com proporção de 1:98 no critério do p99, um classificador que preveja sempre a classe majoritária "
    "atinge 99% de acurácia sendo completamente inútil. O tratamento exige a combinação de três "
    "medidas: definição do limiar de evento por município (nunca global), reamostragem ou ponderação "
    "de classes no treinamento, e avaliação por métricas orientadas à classe minoritária — recall, "
    "F1 e área sob a curva precisão-recall.",
    "A escolha do limiar é, além disso, uma decisão de negócio: o p95 oferece cinco vezes mais exemplos "
    "positivos e um modelo mais estável, ao custo de acionar alertas em situações que não configuram "
    "emergência. Essa relação entre sensibilidade e custo de falso alarme deve ser pactuada com o "
    "cliente antes da definição da variável-alvo."], cor=AZUL)]

E += [PageBreak()]

# ==================================================================== #
# FECHAMENTO
# ==================================================================== #
E += [P("Síntese e encaminhamentos", "h1")]

E += [P("A análise exploratória cumpriu duas funções. Descreveu o comportamento estatístico das 20 "
        "variáveis numéricas da base e, ao fazê-lo, identificou dois defeitos de construção que "
        "comprometeriam qualquer modelo treinado sobre os dados em sua forma atual, além de esclarecer "
        "por que a relação central do projeto não aparece na correlação direta.", "p")]

E += [P("Correções necessárias no pipeline", "h3")]
E += [B("<b>Reagregar a chuva do CEMADEN por média entre estações.</b> A soma atual faz a variável medir "
        "densidade de sensores em vez de precipitação (r = +0,910 com o número de estações). É a "
        "correção de maior prioridade, pois afeta uma das variáveis centrais do projeto."),
      B("<b>Converter a pressão atmosférica em anomalia por estação.</b> Na forma bruta, 99,1% de sua "
        "variância é altitude do município, e não sinal meteorológico."),
      B("<b>Consolidar os blocos redundantes.</b> Manter uma coluna por grandeza física, reduzindo de 20 "
        "para cerca de 10 variáveis independentes, ou derivar a amplitude horária como variável nova.")]

E += [P("Engenharia de variáveis para a próxima sprint", "h3")]
E += [B("<b>Somas móveis de precipitação</b> em janelas de 3, 7, 15, 30 e 60 dias, e versões defasadas "
        "em 1 a 3 dias. É a intervenção de maior retorno demonstrado: eleva a correlação com a vazão de "
        "ρ ≈ 0,04 para ρ = 0,61."),
      B("<b>Decomposição da direção do vento</b> em componentes seno e cosseno, por ser variável "
        "circular."),
      B("<b>Transformação logarítmica</b> da vazão, que a aproxima satisfatoriamente da normalidade, e "
        "tratamento da precipitação em duas partes (ocorrência e intensidade)."),
      B("<b>Variáveis de contexto de bacia</b> — área de drenagem a montante e posição do município no "
        "curso d'água — ausentes da base atual, e que a Seção 3.4.6 indicou serem determinantes para a "
        "vazão.")]

E += [P("Decisões metodológicas decorrentes", "h3")]
E += [B("<b>Condicionar ao município.</b> Estatísticas e modelos agregados subestimam as relações "
        "hidrológicas: cota × vazão tem correlação de 0,437 globalmente e 0,957 dentro de cada "
        "município."),
      B("<b>Particionar treino e validação por ano completo</b>, e não aleatoriamente, dada a forte "
        "autocorrelação temporal e a variabilidade interanual observada na Figura 11."),
      B("<b>Restringir o escopo do modelo de vazão</b> aos 52 municípios com estação fluviométrica, "
        "ou tratar explicitamente a regionalização como problema à parte."),
      B("<b>Definir o limiar de evento com o cliente</b>, explicitando a relação entre sensibilidade do "
        "alerta e custo do falso alarme.")]

E += [Spacer(1, 0.5*cm)]
E += [caixa("Conclusão", [
    "A hipótese que sustenta o projeto — a de que dados de chuva e de nível de rios permitem antecipar "
    "risco de enchente — é <b>sustentada pela análise</b>, mas não na formulação ingênua. A precipitação "
    "de uma hora não prevê a vazão da hora seguinte. O que prevê é o estado de saturação da bacia, "
    "construído ao longo de semanas e representável por acumulados de chuva com defasagem, "
    "condicionados ao município.",
    "Os dois defeitos de construção identificados são corrigíveis com alterações localizadas no código "
    "de integração, sem necessidade de nova coleta. Uma vez corrigidos, a base reúne as condições para "
    "a etapa de modelagem prevista para a Sprint 2."], cor=AZUL)]

E += [Spacer(1, 0.6*cm)]
E += [P("Reprodutibilidade", "h3")]
E += [P("Os scripts que geraram este documento estão em <font name='Sans'>src/eda/</font> e devem ser "
        "executados na ordem numérica. As tabelas de apoio, com todos os valores em precisão completa, "
        "estão em <font name='Sans'>outputs/tabelas/</font>, e as figuras em alta resolução em "
        "<font name='Sans'>outputs/figuras/</font>.", "p")]

E += [tabela(["Script", "Produz"],
    [["<font name='Sans'>_00_carregar.py</font>", "Carga da base com tipos otimizados e cache em formato Parquet"],
     ["<font name='Sans'>_01_perfil.py</font>", "Estatísticas descritivas completas das 20 variáveis numéricas"],
     ["<font name='Sans'>_02_correlacao.py</font>", "Matrizes de Pearson e Spearman e ranking de pares"],
     ["<font name='Sans'>_03_defasagem.py</font>", "Análise de defasagem e de janelas de acumulação (Tabela 3)"],
     ["<font name='Sans'>_04_secao_3_2.py</font>", "Figuras 1 a 5"],
     ["<font name='Sans'>_05_secao_3_4.py</font>", "Figuras 6 a 9"],
     ["<font name='Sans'>_06_cemaden_geo_series.py</font>", "Figuras 10 a 14"],
     ["<font name='Sans'>_07_numeros_texto.py</font>", "Sazonalidade, ciclo diário e estatísticas de raridade (Tabela 4)"],
     ["<font name='Sans'>_08_gerar_pdf.py</font>", "Este documento"]],
    [5.0, 11.4])]

doc.build(E)
print(f"[PDF] {SAIDA}")
print(f"      {os.path.getsize(SAIDA)/1e6:.2f} MB")
