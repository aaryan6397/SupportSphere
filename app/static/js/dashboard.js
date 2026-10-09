document.addEventListener("DOMContentLoaded", () => {
    const filterPanel = document.querySelector(".ticket-filter-panel");

    if (!filterPanel) {
        return;
    }

    const searchInput = document.querySelector("[data-ticket-search]");
    const statusFilter = document.querySelector("[data-ticket-status]");
    const priorityFilter = document.querySelector("[data-ticket-priority]");
    const categoryFilter = document.querySelector("[data-ticket-category]");

    const ticketRows = document.querySelectorAll(".filterable-ticket-row");
    const emptyState = document.querySelector("#filterEmptyState");
    const visibleCount = document.querySelector("#visibleTicketCount");

    if (!searchInput || !statusFilter || !priorityFilter || !categoryFilter) {
        return;
    }

    function applyFilters() {
        const searchValue = searchInput.value.toLowerCase().trim();
        const statusValue = statusFilter.value;
        const priorityValue = priorityFilter.value;
        const categoryValue = categoryFilter.value;

        let visibleTickets = 0;

        ticketRows.forEach((row) => {
            const searchableText = row.dataset.search.toLowerCase();
            const ticketStatus = row.dataset.status;
            const ticketPriority = row.dataset.priority;
            const ticketCategory = row.dataset.category;

            const matchesSearch =
                searchableText.includes(searchValue);

            const matchesStatus =
                statusValue === "all" ||
                ticketStatus === statusValue;

            const matchesPriority =
                priorityValue === "all" ||
                ticketPriority === priorityValue;

            const matchesCategory =
                categoryValue === "all" ||
                ticketCategory === categoryValue;

            const shouldShow =
                matchesSearch &&
                matchesStatus &&
                matchesPriority &&
                matchesCategory;

            row.style.display = shouldShow ? "grid" : "none";

            if (shouldShow) {
                visibleTickets += 1;
            }
        });

        if (visibleCount) {
            visibleCount.textContent = visibleTickets;
        }

        if (emptyState) {
            emptyState.hidden = visibleTickets !== 0;
        }
    }

    searchInput.addEventListener("input", applyFilters);
    statusFilter.addEventListener("change", applyFilters);
    priorityFilter.addEventListener("change", applyFilters);
    categoryFilter.addEventListener("change", applyFilters);

    applyFilters();
});

