# Multilingual Prompting
#
# https://github.com/Pro-GenAI/PromptLang

from utils import attempt_question, model, log

question_name = "x_power_y"
correct_answer = str(52**13)
log("-" * 20 + question_name + ": " + correct_answer)

attempt_question(
    correct_answer,
    "What is 52^13? Return the answer in backticks like `100`. Do not think.",
    key="English",
)
attempt_question(
    correct_answer,
    "52^13 क्या है? `100` जैसे बैकटिक्स में उत्तर लौटाएँ। Do not think.",
    key="Hindi",
)
attempt_question(
    correct_answer,
    "¿Qué es 52^13? Devuelve la respuesta entre comillas simples, como `100`. Do not think.",
    key="Spanish",
)
attempt_question(
    correct_answer,
    "Combien vaut 52^13? Renvoie la réponse entre guillemets inversés, comme `100`. Do not think.",
    key="French",
)
attempt_question(
    correct_answer,
    "Was ist 52^13? Geben Sie die Antwort in Backticks wie `100` zurück. Do not think.",
    key="German",
)

question_name = "math"
correct_answer = str(3 * 3615 - 6723)
log("-" * 20 + question_name + ": " + correct_answer)

attempt_question(
    correct_answer,
    "If you subtract 6723 from thrice the number 15, what is the result? Provide it in backticks like `100`. Do not think.",
    key="English",
)
attempt_question(
    correct_answer,
    "यदि आप संख्या 15 के तिगुने में से 6723 घटाएँ, तो परिणाम क्या होगा? इसे `100` जैसे बैकटिक्स में लिखें। Do not think.",
    key="Hindi",
)
attempt_question(
    correct_answer,
    "Si restas 6723 al triple del número 15, ¿cuál es el resultado? Indícalo entre comillas simples, como `100`. Do not think.",
    key="Spanish",
)
attempt_question(
    correct_answer,
    "Si vous soustrayez 6723 du tripler du nombre 15, quel est le résultat ? Indiquez-le entre guillemets, comme `100`. Do not think.",
    key="French",
)
attempt_question(
    correct_answer,
    "Wenn Sie 6723 von der verdreifachen Zahl 15 abziehen, was ist das Ergebnis? Geben Sie es in Backticks an, z. B. `100`. Do not think.",
    key="German",
)

question_name = "reverse_pulchritudinous"
correct_answer = "pulchritudinous"[::-1]
log("-" * 20 + question_name + ": " + correct_answer)

attempt_question(
    correct_answer,
    'What is the reverse of the word "pulchritudinous"? Return it as a string in backticks like `example`. Do not think.',
    key="English",
)
attempt_question(
    correct_answer,
    '"pulchritudinous" शब्द का उल्टा क्या है? इसे `example` जैसे बैकटिक्स में स्ट्रिंग के रूप में लौटाएँ। Do not think.',
    key="Hindi",
)
attempt_question(
    correct_answer,
    '¿Cuál es el reverso de la palabra "pulchritudinous"? Devuélvelo como una cadena entre comillas simples, como `example`. Do not think.',
    key="Spanish",
)
attempt_question(
    correct_answer,
    'Quel est l\'inverse du mot "pulchritudinous"? Renvoie-le sous forme de chaîne entre guillemets inversés comme `example`. Do not think.',
    key="French",
)
attempt_question(
    correct_answer,
    'Was ist die Umkehrung des Wortes "pulchritudinous"? Geben Sie es als Zeichenfolge mit Backticks zurück, z. B. `example`. Do not think.',
    key="German",
)

question_name = "vowels_pulchritudinous"
count = sum(1 for char in "pulchritudinous" if char in "aeiou")
correct_answer = str(count)
log("-" * 20 + question_name + ": " + correct_answer)

attempt_question(
    correct_answer,
    'How many vowels are in the word "pulchritudinous"? Finally, return a number in backticks like `100`. Do not think.',
    key="English",
)
attempt_question(
    correct_answer,
    '"pulchritudinous" शब्द में कितने स्वर हैं? अंत में, `100` जैसे बैकटिक्स में एक संख्या लौटाएँ। Do not think.',
    key="Hindi",
)
attempt_question(
    correct_answer,
    '¿Cuántas vocales tiene la palabra "pulchritudinous"? Por último, devuelve un número entre comillas simples, como `100`. Do not think.',
    key="Spanish",
)
attempt_question(
    correct_answer,
    'Combien de voyelles y a-t-il dans le mot "pulchritudinous" ? Enfin, renvoyez un nombre entre guillemets inversés comme `100` Do not think.',
    key="French",
)
attempt_question(
    correct_answer,
    'Wie viele Vokale hat das Wort "pulchritudinous"? Geben Sie abschließend eine Zahl in Backticks zurück, z. B. `100`. Do not think.',
    key="German",
)

question_name = "vowels_sesquipedalian"
count = sum(1 for char in "sesquipedalian" if char in "aeiou")
correct_answer = str(count)
log("-" * 20 + question_name + ": " + correct_answer)

attempt_question(
    correct_answer,
    'How many vowels are in the word "sesquipedalian"? Finally, return a number in backticks like `100`. Do not think.',
    key="English",
)
attempt_question(
    correct_answer,
    '"sesquipedalian" शब्द में कितने स्वर हैं? अंत में, `100` जैसे बैकटिक्स में एक संख्या लौटाएँ। Do not think.',
    key="Hindi",
)
attempt_question(
    correct_answer,
    '¿Cuántas vocales tiene la palabra "sesquipedalian"? Por último, devuelve un número entre comillas simples, como `100`. Do not think.',
    key="Spanish",
)
attempt_question(
    correct_answer,
    'Combien de voyelles y a-t-il dans le mot "sesquipedalian" ? Enfin, renvoyez un nombre entre guillemets inversés comme `100` Do not think.',
    key="French",
)
attempt_question(
    correct_answer,
    'Wie viele Vokale hat das Wort "sesquipedalian"? Geben Sie abschließend eine Zahl in Backticks zurück, z. B. `100`. Do not think.',
    key="German",
)
