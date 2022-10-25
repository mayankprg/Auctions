
document.addEventListener('DOMContentLoaded', ()=>{

    const main = document.querySelector('main');
    if (document.querySelector('.alert') !== null) {
        main.style.paddingTop = '0';
    } 

    document.addEventListener('click', event => {
        const element = event.target;
        if (element.className === 'close') {
            element.parentElement.remove();
            main.style.paddingTop = '80px';
        };
    });


});

