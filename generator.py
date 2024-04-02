from flask import Flask, request, make_response
from fpdf import FPDF

app = Flask(__name__)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Curriculum Vitae', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Página ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, label):
        self.set_fill_color(200, 220, 255) 
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, label, 0, 1, 'L', 1)
        self.ln(2)

    def chapter_subtitle(self, subtitle):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, subtitle, 0, 1)
        self.ln(1)

    def chapter_body(self, body):
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, body)
        self.ln()

@app.route('/generate-cv', methods=['POST'])
def generate_cv():

    data = request.json

    pdf = PDF()
    pdf.add_page()

    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    pdf.chapter_title('Informações Pessoais')
    info_pessoais = f"Nome: {data['nome']}\nIdade: {data['idade']}\nEmail: {data['email']}\nTelefone: {data['telefone']}"
    pdf.chapter_body(info_pessoais)

    pdf.chapter_title('Educação')
    educacao = f"Graduação: {data['graduacao']}\nEnsino Médio: {data['ensino_medio']}"
    pdf.chapter_body(educacao)

    pdf.chapter_title('Sobre')
    sobre_descricao = ""
    for sobre in data['sobre']:
        sobre_descricao += f"{sobre['descricao']}\n"
    pdf.chapter_body(sobre_descricao)

    pdf.chapter_title('Experiência Profissional')
    experiencia = ""
    for exp in data['experiencia']:
        experiencia += f"{exp['titulo']} - {exp['empresa']} ({exp['inicio']} - {exp['fim']})\n"
    for subtitulo in exp['subtitulo']:
        experiencia += f"    {subtitulo}\n"
    experiencia += "\n"
    pdf.chapter_body(experiencia)

    pdf.chapter_title('Habilidades')
    habilidades = '\n'.join(data['habilidades'])
    pdf.chapter_body(habilidades)

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename={data['nome']}_curriculo.pdf"
    return response

if __name__ == '__main__':
    app.run(debug=True)
