// Initialize Flatpickr Date Picker for Month/Year selection
document.addEventListener('DOMContentLoaded', function() {
    const monthYearInput = document.getElementById('month_year');
    const yearInput = document.getElementById('publication_year');
    
    // Month/Year Picker
    if (monthYearInput) {
        flatpickr(monthYearInput, {
            mode: 'single',
            type: 'text',
            dateFormat: 'm/Y',  // Format: MM/YYYY
            minDate: '2000-01-01',
            maxDate: '2030-12-31',
            showMonths: 1,
            static: false,
            inline: false,
            enableTime: false,
            
            // Month/Year mode styling
            monthSelectorType: 'static',
            
            // Custom configuration for better UX
            locale: {
                firstDayOfWeek: 0
            },
            
            // Customize the calendar appearance
            onReady: function(selectedDates, dateStr, instance) {
                // Add custom classes for styling
                const calendarContainer = instance.calendarContainer;
                if (calendarContainer) {
                    calendarContainer.classList.add('custom-calendar');
                }
            },
            
            // On date selection
            onChange: function(selectedDates, dateStr, instance) {
                if (selectedDates.length > 0) {
                    const date = selectedDates[0];
                    const month = String(date.getMonth() + 1).padStart(2, '0');
                    const year = date.getFullYear();
                    monthYearInput.value = month + '/' + year;
                }
            }
        });
    }
    
    // Year Picker
    if (yearInput) {
        flatpickr(yearInput, {
            mode: 'single',
            type: 'text',
            dateFormat: 'Y',  // Format: YYYY
            minDate: '2000-01-01',
            maxDate: '2030-12-31',
            showMonths: 1,
            static: false,
            inline: false,
            enableTime: false,
            
            // Year-only mode
            monthSelectorType: 'static',
            
            locale: {
                firstDayOfWeek: 0
            },
            
            // Customize year picker appearance
            onReady: function(selectedDates, dateStr, instance) {
                const calendarContainer = instance.calendarContainer;
                if (calendarContainer) {
                    calendarContainer.classList.add('year-picker-calendar');
                }
            },
            
            // On year selection
            onChange: function(selectedDates, dateStr, instance) {
                if (selectedDates.length > 0) {
                    const date = selectedDates[0];
                    const year = date.getFullYear();
                    yearInput.value = year;
                }
            }
        });
    }
});
