
const id_a = document.getElementById('a');

// write a function that returns the next letter in the alphabet for a given letter
// nextLetter('a') === 'b'
// nextLetter('z') === 'a'
const nextLetter = (letter) => {
    const alphabet = 'abcdefghijklmnopqrstuvwxyz';
    const index = alphabet.indexOf(letter);
    const nextIndex = (index + 1) % alphabet.length;
    return alphabet[nextIndex];
}
id_a.innerText = "a";
for (;;) {
    setTimeout(()=> {
        id_a.innerText = nextLetter(id_a.innerText);
    }, 100)
}
