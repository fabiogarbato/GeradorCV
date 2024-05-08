from flask import Flask, request, make_response
from fpdf import FPDF

app = Flask(__name__)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, self.lang_titles['cv_title'], 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, self.lang_titles['page_label'] + str(self.page_no()), 0, 0, 'C')

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
    language = data.get('language', 'en')  # Default to English if not specified

    # Define titles and field names based on language
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
    pdf.add_page()

    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    pdf.chapter_title(lang_keys['personal_info'])
    personal_info = f"Name: {data[lang_keys['name']]}\nAge: {data[lang_keys['age']]}\nCity: {data[lang_keys['city']]}\nEmail: {data[lang_keys['email']]}\nPhone: {data[lang_keys['phone']]}"
    pdf.chapter_body(personal_info)

    pdf.chapter_title(lang_keys['education'])
    education = f"College: {data.get('college', '')}\nHigh School: {data.get('high_school', '')}"
    pdf.chapter_body(education)

    pdf.chapter_title(lang_keys['professional_summary'])
    summary_description = "\n".join([desc['descricao' if language == 'pt' else 'description'] for desc in data[lang_keys['about']]])
    pdf.chapter_body(summary_description)

    pdf.chapter_title(lang_keys['professional_experience'])
    for exp in data[lang_keys['experience']]:
        pdf.chapter_subtitle(exp['empresa' if language == 'pt' else 'company'])
        for position in exp[lang_keys['positions']]:
            experience = f"{position['titulo' if language == 'pt' else 'title']} - {position['inicio' if language == 'pt' else 'start']} - {position['fim' if language == 'pt' else 'end']}\n"
            experience += "\n".join([f"    {detail}" for detail in position[lang_keys['details']]])
            pdf.chapter_body(experience)

    pdf.chapter_title(lang_keys['skills'])
    skills = '\n'.join(data['habilidades' if language == 'pt' else 'skills'])
    pdf.chapter_body(skills)

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f"attachment; filename={data[lang_keys['name']]}_resume.pdf"
    return response

if __name__ == '__main__':
    app.run(debug=True)
