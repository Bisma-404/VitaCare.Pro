/**
 * VitaCare Pro - Table Utilities
 * Sortable, filterable, and exportable tables
 */

class TableUtility {
    constructor(tableId) {
        this.table = document.getElementById(tableId);
        if (!this.table) {
            console.error(`Table with id "${tableId}" not found`);
            return;
        }
        this.tbody = this.table.querySelector('tbody');
        this.thead = this.table.querySelector('thead');
        this.init();
    }

    init() {
        this.makeSortable();
    }

    makeSortable() {
        const headers = this.thead.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.classList.add('sortable');
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => this.sortTable(index));
        });
    }

    sortTable(columnIndex) {
        const rows = Array.from(this.tbody.querySelectorAll('tr'));
        const headers = this.thead.querySelectorAll('th');
        const currentHeader = headers[columnIndex];

        // Determine sort direction
        const isAscending = !currentHeader.classList.contains('asc');

        // Remove sort classes from all headers
        headers.forEach(h => h.classList.remove('asc', 'desc'));

        // Add sort class to current header
        currentHeader.classList.add(isAscending ? 'asc' : 'desc');

        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();

            // Try to parse as numbers
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);

            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }

            // String comparison
            return isAscending
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        });

        // Re-append sorted rows
        rows.forEach(row => this.tbody.appendChild(row));
    }

    filter(searchTerm) {
        const rows = this.tbody.querySelectorAll('tr');
        const lowerSearch = searchTerm.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(lowerSearch) ? '' : 'none';
        });
    }

    exportToCSV(filename = 'export.csv') {
        const rows = [];

        // Get headers
        const headers = Array.from(this.thead.querySelectorAll('th'))
            .map(th => th.textContent.trim());
        rows.push(headers);

        // Get data rows
        const dataRows = this.tbody.querySelectorAll('tr');
        dataRows.forEach(row => {
            if (row.style.display !== 'none') {
                const cells = Array.from(row.querySelectorAll('td'))
                    .map(td => td.textContent.trim());
                rows.push(cells);
            }
        });

        // Create CSV
        const csv = rows.map(row =>
            row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',')
        ).join('\n');

        // Download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);

        toast.success('Table exported successfully!');
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TableUtility;
}
