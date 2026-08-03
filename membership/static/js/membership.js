document.addEventListener("DOMContentLoaded", function () {
    // --------------------------------------------------
    // Application type switching
    // --------------------------------------------------
    const applicationType = document.getElementById(
        "id_application_type"
    );

    const individualSection = document.getElementById(
        "individual-application-section"
    );

    const corporateSection = document.getElementById(
        "corporate-application-section"
    );

    function toggleApplicationSections() {
        if (!applicationType) {
            return;
        }

        const selectedType = applicationType.value;

        if (individualSection) {
            individualSection.style.display =
                selectedType === "individual" ? "block" : "none";
        }

        if (corporateSection) {
            corporateSection.style.display =
                selectedType === "corporate" ? "block" : "none";
        }
    }

    if (applicationType) {
        applicationType.addEventListener(
            "change",
            toggleApplicationSections
        );

        toggleApplicationSections();
    }


    // --------------------------------------------------
    // Select all checkboxes
    // --------------------------------------------------
    const selectAllCheckbox = document.getElementById(
        "select-all"
    );

    const rowCheckboxes = document.querySelectorAll(
        ".row-checkbox"
    );

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener(
            "change",
            function () {
                rowCheckboxes.forEach(function (checkbox) {
                    checkbox.checked =
                        selectAllCheckbox.checked;
                });

                updateBulkActionButtons();
            }
        );
    }

    rowCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener(
            "change",
            function () {
                if (!selectAllCheckbox) {
                    return;
                }

                const allSelected = Array.from(
                    rowCheckboxes
                ).every(function (item) {
                    return item.checked;
                });

                selectAllCheckbox.checked = allSelected;

                updateBulkActionButtons();
            }
        );
    });


    // --------------------------------------------------
    // Bulk action controls
    // --------------------------------------------------
    function updateBulkActionButtons() {
        const selectedRows = document.querySelectorAll(
            ".row-checkbox:checked"
        );

        const bulkActionElements =
            document.querySelectorAll(
                "[data-bulk-action]"
            );

        bulkActionElements.forEach(function (element) {
            element.disabled =
                selectedRows.length === 0;
        });
    }

    updateBulkActionButtons();


    // --------------------------------------------------
    // Confirm single delete
    // --------------------------------------------------
    const deleteButtons = document.querySelectorAll(
        "[data-delete-url]"
    );

    deleteButtons.forEach(function (button) {
        button.addEventListener(
            "click",
            function () {
                const deleteUrl =
                    button.dataset.deleteUrl;

                const itemName =
                    button.dataset.itemName ||
                    "this record";

                const confirmed = window.confirm(
                    `Are you sure you want to delete ${itemName}?`
                );

                if (confirmed && deleteUrl) {
                    window.location.href = deleteUrl;
                }
            }
        );
    });


    // --------------------------------------------------
    // Automatically close alerts
    // --------------------------------------------------
    const alerts = document.querySelectorAll(
        ".membership-alert"
    );

    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.classList.add("is-hidden");

            setTimeout(function () {
                alert.remove();
            }, 300);
        }, 5000);
    });


    // --------------------------------------------------
    // Table search
    // --------------------------------------------------
    const tableSearchInputs =
        document.querySelectorAll(
            "[data-table-search]"
        );

    tableSearchInputs.forEach(function (input) {
        input.addEventListener(
            "input",
            function () {
                const tableId =
                    input.dataset.tableSearch;

                const table =
                    document.getElementById(tableId);

                if (!table) {
                    return;
                }

                const searchValue =
                    input.value
                        .toLowerCase()
                        .trim();

                const rows =
                    table.querySelectorAll("tbody tr");

                rows.forEach(function (row) {
                    const rowText =
                        row.textContent
                            .toLowerCase();

                    row.style.display =
                        rowText.includes(searchValue)
                            ? ""
                            : "none";
                });
            }
        );
    });


    // --------------------------------------------------
    // Form submit protection
    // --------------------------------------------------
    const membershipForms =
        document.querySelectorAll(
            "form[data-membership-form]"
        );

    membershipForms.forEach(function (form) {
        form.addEventListener(
            "submit",
            function () {
                const submitButton =
                    form.querySelector(
                        'button[type="submit"]'
                    );

                if (submitButton) {
                    submitButton.disabled = true;

                    submitButton.dataset.originalText =
                        submitButton.innerHTML;

                    submitButton.innerHTML =
                        "Processing...";
                }
            }
        );
    });


    // --------------------------------------------------
    // Modal data handling
    // --------------------------------------------------
    const modalTriggers =
        document.querySelectorAll(
            "[data-membership-modal]"
        );

    modalTriggers.forEach(function (trigger) {
        trigger.addEventListener(
            "click",
            function () {
                const modalId =
                    trigger.dataset.membershipModal;

                const modal =
                    document.getElementById(modalId);

                if (!modal) {
                    return;
                }

                modal.classList.add("is-open");

                document.body.classList.add(
                    "modal-open"
                );
            }
        );
    });

    const modalCloseButtons =
        document.querySelectorAll(
            "[data-close-membership-modal]"
        );

    modalCloseButtons.forEach(function (button) {
        button.addEventListener(
            "click",
            function () {
                const modal =
                    button.closest(
                        ".membership-modal"
                    );

                if (modal) {
                    modal.classList.remove(
                        "is-open"
                    );
                }

                document.body.classList.remove(
                    "modal-open"
                );
            }
        );
    });


    // --------------------------------------------------
    // Close modal when clicking outside
    // --------------------------------------------------
    document.addEventListener(
        "click",
        function (event) {
            const openModals =
                document.querySelectorAll(
                    ".membership-modal.is-open"
                );

            openModals.forEach(function (modal) {
                if (event.target === modal) {
                    modal.classList.remove(
                        "is-open"
                    );

                    document.body.classList.remove(
                        "modal-open"
                    );
                }
            });
        }
    );


    // --------------------------------------------------
    // Close modal with Escape key
    // --------------------------------------------------
    document.addEventListener(
        "keydown",
        function (event) {
            if (event.key === "Escape") {
                const openModals =
                    document.querySelectorAll(
                        ".membership-modal.is-open"
                    );

                openModals.forEach(
                    function (modal) {
                        modal.classList.remove(
                            "is-open"
                        );
                    }
                );

                document.body.classList.remove(
                    "modal-open"
                );
            }
        }
    );
});


