import streamlit as st
from groq import Groq
import json
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Interactive Learning Buddy",
    page_icon="📘",
    layout="wide"
)

# ---------------- API KEY ----------------
api_key = st.sidebar.text_input(
    "Enter your Groq API Key:",
    type="password"
)

# ---------------- LEARN FUNCTION ----------------
def ask_groq(prompt):

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {e}"

# ---------------- QUIZ FUNCTION ----------------
def generate_quiz(subject):

    try:
        client = Groq(api_key=api_key)

        prompt = f"""
Generate 10 multiple choice quiz questions on {subject}.

Return ONLY in valid JSON format like this:

[
 {{
   "question":"...",
   "options":["A) ...","B) ...","C) ...","D) ..."],
   "answer":"A",
   "explanation":"..."
 }}
]

Do not return extra text.
"""

        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
        )

        text = response.choices[0].message.content.strip()

        start = text.find("[")
        end = text.rfind("]") + 1

        clean_json = text[start:end]

        clean_json = clean_json.replace(",]", "]")
        clean_json = clean_json.replace(",}", "}")

        quiz_data = json.loads(clean_json)

        return quiz_data

    except Exception as e:
        st.error(f"Quiz Generation Error: {e}")
        return None

# ---------------- SESSION STATE ----------------
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

# ---------------- TITLE ----------------
st.title("📘 Interactive Learning Buddy")

tab1, tab2 = st.tabs(["📖 Learn", "📝 Smart Quiz"])

# ---------------- LEARN TAB ----------------
with tab1:

    topic = st.text_input("Enter topic to learn:")

    if st.button("Learn Now"):

        if not api_key:
            st.error("Enter API key first")

        elif not topic:
            st.warning("Enter topic")

        else:

            result = ask_groq(
                f"Explain {topic} in simple student friendly language"
            )

            st.success("Explanation:")
            st.write(result)

# ---------------- QUIZ TAB ----------------
with tab2:

    subject = st.text_input("Enter subject for quiz:")

    if st.button("Generate Quiz"):

        if not api_key:
            st.error("Enter API key first")

        elif not subject:
            st.warning("Enter subject")

        else:

            with st.spinner("Generating Smart Quiz..."):

                st.session_state.quiz_data = generate_quiz(subject)

    if st.session_state.quiz_data:

        user_answers = []

        st.subheader("Answer all questions:")

        for i, q in enumerate(st.session_state.quiz_data):

            st.markdown(f"### Q{i+1}. {q['question']}")

            ans = st.radio(
                "Choose your answer:",
                q["options"],
                key=f"q_{i}"
            )

            user_answers.append(ans)

        if st.button("Submit Quiz"):

            score = 0

            for i, q in enumerate(st.session_state.quiz_data):

                selected_option = user_answers[i]

                correct_letter = q["answer"]

                if selected_option.startswith(correct_letter):
                    score += 1

            total = len(st.session_state.quiz_data)
            wrong = total - score
            percent = (score / total) * 100

            # ---------------- ANALYTICS ----------------

            st.markdown("---")
            st.header("📊 Quiz Analytics Result")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("✅ Correct", score)

            with col2:
                st.metric("❌ Wrong", wrong)

            with col3:
                st.metric("📈 Percentage", f"{percent:.1f}%")

            # ---------------- PROGRESS BAR ----------------

            st.subheader("Performance Meter")

            st.progress(int(percent))

            if percent >= 80:
                st.success("Performance: Excellent")

            elif percent >= 50:
                st.warning("Performance: Good")

            else:
                st.error("Performance: Needs Improvement")

            # ---------------- PIE CHART ----------------

            st.subheader("📊 Quiz Performance Graph")

            fig, ax = plt.subplots()

            labels = ["Correct", "Wrong"]
            sizes = [score, wrong]

            ax.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%"
            )

            ax.axis("equal")

            st.pyplot(fig)

            # ---------------- QUICK RESULT ----------------

            st.subheader("📋 Quick Quiz Review")

            for i, q in enumerate(st.session_state.quiz_data):

                selected_option = user_answers[i]

                correct_letter = q["answer"]

                if selected_option.startswith(correct_letter):

                    st.success(
                        f"Q{i+1} ✅ Your Answer: {selected_option} | Correct Answer: {correct_letter}"
                    )

                else:

                    st.error(
                        f"Q{i+1} ❌ Your Answer: {selected_option} | Correct Answer: {correct_letter}"
                    )

            # ---------------- DETAILED REVIEW ----------------

            st.markdown("---")
            st.header("📑 Detailed Answer Review")

            for i, q in enumerate(st.session_state.quiz_data):

                selected_option = user_answers[i]

                correct_letter = q["answer"]

                st.markdown(f"### Q{i+1}. {q['question']}")

                st.write(f"Your Answer: {selected_option}")

                st.write(f"Correct Answer: {correct_letter}")

                st.write(f"Explanation: {q['explanation']}")

                if selected_option.startswith(correct_letter):
                    st.success("Correct")

                else:
                    st.error("Wrong")

                st.markdown("---")