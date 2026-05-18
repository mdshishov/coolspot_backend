document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        document.querySelectorAll('.add-row a').forEach(el => {
            el.textContent = el.textContent.replace(/Добавить ещ[её] один\s+/i, '');
        });

        const addBtn = document.querySelector('.object-tools a');
        if (addBtn) addBtn.textContent = addBtn.textContent.replace(/Добавить/i, 'Нов.');

        if (window.location.pathname.includes('delete')) {
            const deleteMsg = document.querySelector('#content p');
            if (deleteMsg) deleteMsg.textContent = deleteMsg.textContent.replace(/ типа.*\?/i, '?');
        }

        const contentH1 = document.querySelector('#content h1');
        if (contentH1) {
            contentH1.textContent = contentH1.textContent.replace(
                /Выберите\s+.+?\s+для изменения/,
                'Выберите объект для изменения'
            );
        }
    }, 0);
});