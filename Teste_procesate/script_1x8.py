import re

def parse_exercises(content):
    # Split the file into exercises by '----'
    exercises = [e.strip() for e in content.split('----') if e.strip()]
    return exercises

def parse_exercise(exercise):
    # Separate parts: text, options, answers
    parts = re.split(r'\*{4,}|\={4,}', exercise)
    # parts: [text, options, answers], but need to find which is which
    text = options = answers = None
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Guess based on structure
        if re.search(r'\(\d+\) \.\.\.\.', part):  # text with gaps
            text = part
        elif re.match(r'\d+ [A-D] ', part):  # options line
            options = part
        elif re.search(r'one mark for each correct answer', part):
            answers = part
    return text, options, answers

def parse_options(options_text):
    # Returns {gap_number: {A: option1, B: option2, ...}}
    options = {}
    for line in options_text.strip().split('\n'):
        m = re.match(r'(\d+)\s+', line)
        if not m:
            continue
        num = int(m.group(1))
        # Remove the number from the line
        rest = line[m.end():]
        # Find all letter-option pairs: A text B text C text D text
        parts = re.split(r'([A-D]) ', rest)
        # parts = ['', 'A', 'option for A', 'B', 'option for B', ...]
        choices = {}
        for i in range(1, len(parts)-1, 2):
            ch = parts[i]
            txt = parts[i+1].strip()
            choices[ch] = txt
        options[num] = choices
    return options

def parse_answers(answers_text):
    # Returns {gap_number: 'A'/'B'/...}
    # Find the answer line after the explanatory header
    ans_lines = []
    for line in answers_text.strip().split('\n'):
        if re.match(r'\d+ [A-D]', line):
            ans_lines.append(line)
    if not ans_lines:
        # maybe everything is on one line
        all_text = answers_text.strip()
        m = re.search(r'\d+ [A-D].*', all_text)
        if m:
            ans_lines = [m.group(0)]
    # flatten to pairs
    answers = {}
    for line in ans_lines:
        for pair in re.findall(r'(\d+) ([A-D])', line):
            answers[int(pair[0])] = pair[1]
    return answers

# Pentru a nu da skip la (0) pui skip_zero=False in fill_text
def fill_text(text, options, answers, skip_zero=True):
    def replacer(match):
        num = int(match.group(1))
        # If skip_zero is True and num == 0, leave it as is
        if skip_zero and num == 0:
            return match.group(0)
        ans_letter = answers.get(num)
        if ans_letter and num in options and ans_letter in options[num]:
            return options[num][ans_letter]
        else:
            return match.group(0) # Leave the gap untouched if no answer/option
    pattern = re.compile(r'\((\d+)\)\s*\.+')
    filled = pattern.sub(replacer, text)
    return filled


def process_file(input_path, output_path):
    with open(input_path, encoding='utf8') as f:
        content = f.read()

    exercises = parse_exercises(content)
    filled_texts = []

    for ex in exercises:
        text, options, answers = parse_exercise(ex)
        if not (text and options and answers):
            continue
        options_map = parse_options(options)
        answers_map = parse_answers(answers)
        #Aici poti pune inca un parametru skip_zero=False daca vrei sa nu dai skip la (0)
        # de exemplu: filled = fill_text(text, options_map, answers_map, skip_zero=False)
        filled = fill_text(text, options_map, answers_map)
        filled_texts.append(filled.strip())

    with open(output_path, 'w', encoding='utf8') as f:
        f.write('\n\n'.join(filled_texts))

if __name__ == "__main__":
    # Usage: replace 'input.txt' and 'output.txt' as needed
    process_file('C:\\Proiecte\\EnglezaLLM\\Teste_procesate\\CPE_1x8.txt', 'C:\\Proiecte\\EnglezaLLM\\Teste_procesate\\filled_texts.txt')
