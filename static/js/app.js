function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find((row) => row.startsWith(`${name}=`));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
}

function initTaskFilters() {
    const taskSearch = document.querySelector('#taskSearch');
    const statusFilter = document.querySelector('#statusFilter');
    const taskCards = document.querySelectorAll('.task-card');

    if (!taskSearch || !statusFilter || !taskCards.length) {
        return;
    }

    const applyFilter = () => {
        const query = taskSearch.value.trim().toLowerCase();
        const status = statusFilter.value;

        taskCards.forEach((card) => {
            const matchesQuery = card.dataset.search.includes(query);
            const matchesStatus = status === 'all' || card.dataset.status === status;
            card.hidden = !(matchesQuery && matchesStatus);
        });
    };

    taskSearch.addEventListener('input', applyFilter);
    statusFilter.addEventListener('change', applyFilter);
}

function initStatusToggle() {
    const buttons = document.querySelectorAll('.js-toggle-status');
    if (!buttons.length) {
        return;
    }

    buttons.forEach((button) => {
        button.addEventListener('click', async () => {
            button.disabled = true;
            try {
                const response = await fetch(button.dataset.url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });
                if (!response.ok) {
                    throw new Error('Unable to update task status.');
                }
                window.location.reload();
            } catch (error) {
                alert(error.message);
            } finally {
                button.disabled = false;
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initTaskFilters();
    initStatusToggle();
});
