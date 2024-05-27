from flask import Flask, request, make_response
from fpdf import FPDF

app = Flask(__name__)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, self.lang_titles['cv_title'], 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'{self.page_no()} / {{nb}}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_fill_color(220, 220, 220)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, label, 0, 1, 'L', 1)
        self.ln(1)

    def chapter_subtitle(self, subtitle):
        self.set_font('Arial', 'B', 11)
        self.cell(0, 5, subtitle, 0, 1)
        self.ln(1)

    def chapter_body(self, body):
        self.set_font('Arial', '', 8)
        self.multi_cell(0, 4, body)
        self.ln()

@app.route('/generate-cv', methods=['POST'])
def generate_cv():
    data = request.json
    language = data.get('linguagem', 'en')

    lang_keys = {
        'pt': {
            'cv_title': 'Curriculum Vitae', 'page_label': 'Página ', 'personal_info': 'Informações Pessoais',
            'education': 'Educação', 'professional_summary': 'Resumo Profissional',
            'professional_experience': 'Experiência Profissional', 'skills': 'Habilidades',
            'name': 'nome', 'age': 'idade', 'city': 'cidade', 'email': 'email', 'phone': 'telefone',
            'about': 'sobre', 'experience': 'experiencia', 'positions': 'cargos', 'details': 'subtitulo'
        },
        'en': {
            'cv_title': 'Resume', 'page_label': 'Page ', 'personal_info': 'Personal Information',
            'education': 'Education', 'professional_summary': 'Professional Summary',
            'professional_experience': 'Professional Experience', 'skills': 'Skills',
            'name': 'name', 'age': 'age', 'city': 'city', 'email': 'email', 'phone': 'phone',
            'about': 'about', 'experience': 'experience', 'positions': 'positions', 'details': 'details'
        }
    }[language]

    pdf = PDF()
    pdf.lang_titles = lang_keys
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    pdf.chapter_title(lang_keys['personal_info'])
    personal_info = (
        f"{lang_keys['name'].capitalize()}: {data.get(lang_keys['name'], 'N/A')}\n"
        f"{lang_keys['age'].capitalize()}: {data.get(lang_keys['age'], 'N/A')}\n"
        f"{lang_keys['city'].capitalize()}: {data.get(lang_keys['city'], 'N/A')}\n"
        f"{lang_keys['email'].capitalize()}: {data.get(lang_keys['email'], 'N/A')}\n"
        f"{lang_keys['phone'].capitalize()}: {data.get(lang_keys['phone'], 'N/A')}"
    )
    pdf.chapter_body(personal_info)

    pdf.chapter_title(lang_keys['education'])
    education_data = data.get('educacao' if language == 'pt' else 'education', {})
    education_lines = []

    for key, values in education_data.items():
        for value in values:
            education_lines.append(f"{key.replace('_', ' ').title()}: {value}")

    education = "\n".join(education_lines)
    pdf.chapter_body(education)

    pdf.chapter_title(lang_keys['professional_summary'])
    summary_description = "\n".join([desc['descricao' if language == 'pt' else 'description'] for desc in data.get(lang_keys['about'], [])])
    pdf.chapter_body(summary_description)

    pdf.chapter_title(lang_keys['professional_experience'])
    for exp in data.get(lang_keys['experience'], []):
        pdf.chapter_subtitle(exp['empresa' if language == 'pt' else 'company'])
        for position in exp[lang_keys['positions']]:
            experience = (
                f"{position['titulo' if language == 'pt' else 'title']} - "
                f"{position['inicio' if language == 'pt' else 'start']} - "
                f"{position['fim' if language == 'pt' else 'end']}\n"
                + "\n".join([f"    {detail}" for detail in position[lang_keys['details']]])
            )
            pdf.chapter_body(experience)

    pdf.chapter_title(lang_keys['skills'])
    skills = '\n'.join(data.get('habilidades' if language == 'pt' else 'skills', []))
    pdf.chapter_body(skills)

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename={data.get(lang_keys['name'], 'resume')}_resume.pdf"
    return response

if __name__ == '__main__':
    app.run(debug=True)
