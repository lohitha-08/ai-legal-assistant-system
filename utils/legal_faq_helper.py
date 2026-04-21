import re


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower().strip())


def make_result(question, answer):
    return {
        "question": question,
        "answer": answer
    }


def get_faq_answer(user_query):
    q = normalize_text(user_query)

    if "fir" in q:
        return make_result(
            "What is FIR?",
            "FIR means First Information Report. It is a written complaint given to police about a cognizable offence."
        )

    elif "bail" in q:
        return make_result(
            "What is Bail?",
            "Bail is the temporary release of an accused person while the case is under legal process."
        )

    elif "arrest" in q:
        return make_result(
            "What are Arrest Rights?",
            "A person generally has the right to know the reason for arrest, contact a lawyer or family member, and be treated according to legal procedure."
        )

    elif "complaint" in q:
        return make_result(
            "How to file complaint?",
            "You can file a complaint at the nearest police station or proper online portal by giving incident details, date, place, and proof if available."
        )

    elif "court" in q:
        return make_result(
            "How does court process work?",
            "A case may go through complaint, investigation, filing of charge sheet, trial, and judgment depending on the nature of the matter."
        )

    else:
        return make_result(
            "General Legal Help",
            "Please explain your legal issue more clearly to get better guidance."
        )