from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)
questions = []
index = 0
score = 0
total_attempts = 0
correct_answer = None
subjects = {
    "anciano": ["tema2", "tema3","tema4","tema5","tema6"],  
    "joven": ["tema1", "tema2"],
    "adulto": ["tema1", "tema2", "tema3"],
    "etica": ["tema1", "tema2"]
}

def load_questions(subject, theme):
    global questions
    questions = []
    with open(f"asignaturas/{subject}/{theme}.txt", encoding='utf-8') as f:
        lines = f.readlines()

    for i in range(0, len(lines), 6):  
        if i + 5 < len(lines): 
            question_text = lines[i].strip()
            choices = [lines[i+j].strip() for j in range(1, 5)]
            try:
                answer = [choice.endswith('*') for choice in choices].index(True)
                choices[answer] = choices[answer].rstrip('*')
            except ValueError:
                continue
            questions.append({"question": question_text, "choices": choices, "answer": answer})
    
    random.shuffle(questions)
    questions = questions[:10]


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        subject_theme = request.form['theme'].split('/')
        return redirect(url_for('quiz', subject=subject_theme[0], theme=subject_theme[1]))
    return render_template('home.html', subjects=subjects)

@app.route('/quiz/<subject>/<theme>', methods=["GET", "POST"])
def quiz(subject, theme):
    global index, score, total_attempts, correct_answer
    if not questions:
        load_questions(subject, theme)

    if request.method == "POST":
        answer = request.form.get('answer')
        correct_answer = questions[index]['answer']

        total_attempts += 1

        if int(answer) == correct_answer:
            score += 1
            index += 1
            return redirect(url_for('correct', subject=subject, theme=theme))

        index += 1
        return redirect(url_for('incorrect', subject=subject, theme=theme, answer=correct_answer + 1))

    if index == len(questions):
        final_score = score
        final_total_attempts = total_attempts
        index, score, total_attempts = 0, 0, 0  # reset
        questions.clear()  # clear the questions
        return render_template("scores.html", score=final_score, total_attempts=final_total_attempts)


    return render_template("quiz.html", question=questions[index], score=score, total_attempts=total_attempts, index=index)

@app.route("/correct/<subject>/<theme>")
def correct(subject, theme):
    global index, score, total_attempts
    return render_template("correct.html", score=score, total_attempts=total_attempts, index=index, subject=subject, theme=theme)


@app.route("/incorrect/<subject>/<theme>/<int:answer>")
def incorrect(subject, theme, answer):
    global index, score, total_attempts
    correct_option = questions[index - 1]['choices'][answer - 1]  # Retrieve correct option text
    question_text = questions[index-1]['question']  # get previous question's text
    return render_template("incorrect.html", score=score, total_attempts=total_attempts, index=index, answer=answer, question_text=question_text, correct_option=correct_option, subject=subject, theme=theme)

if __name__ == "__main__":
    app.run(debug=True)