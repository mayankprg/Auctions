document.addEventListener('click', event => {
    const element = event.target;
    if (element.className === 'close') {
        element.parentElement.remove();
    };
});


