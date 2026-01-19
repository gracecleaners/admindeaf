/**
 * Country Code Selector for Phone Numbers
 * Provides a dropdown with country codes and flags for phone number input
 */

class CountryCodeSelector {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            defaultCountry: 'UG',
            placeholder: 'Select country',
            showFlags: true,
            searchEnabled: true,
            ...options
        };
        
        this.countries = [
            { code: 'UG', name: 'Uganda', flag: '🇺🇬', dialCode: '+256' },
            { code: 'KE', name: 'Kenya', flag: '🇰🇪', dialCode: '+254' },
            { code: 'TZ', name: 'Tanzania', flag: '🇹🇿', dialCode: '+255' },
            { code: 'RW', name: 'Rwanda', flag: '🇷🇼', dialCode: '+250' },
            { code: 'BI', name: 'Burundi', flag: '🇧🇮', dialCode: '+257' },
            { code: 'SS', name: 'South Sudan', flag: '🇸🇸', dialCode: '+211' },
            { code: 'ET', name: 'Ethiopia', flag: '🇪🇹', dialCode: '+251' },
            { code: 'SO', name: 'Somalia', flag: '🇸🇴', dialCode: '+252' },
            { code: 'DJ', name: 'Djibouti', flag: '🇩🇯', dialCode: '+253' },
            { code: 'ER', name: 'Eritrea', flag: '🇪🇷', dialCode: '+291' },
            { code: 'US', name: 'United States', flag: '🇺🇸', dialCode: '+1' },
            { code: 'GB', name: 'United Kingdom', flag: '🇬🇧', dialCode: '+44' },
            { code: 'CA', name: 'Canada', flag: '🇨🇦', dialCode: '+1' },
            { code: 'AU', name: 'Australia', flag: '🇦🇺', dialCode: '+61' },
            { code: 'DE', name: 'Germany', flag: '🇩🇪', dialCode: '+49' },
            { code: 'FR', name: 'France', flag: '🇫🇷', dialCode: '+33' },
            { code: 'IT', name: 'Italy', flag: '🇮🇹', dialCode: '+39' },
            { code: 'ES', name: 'Spain', flag: '🇪🇸', dialCode: '+34' },
            { code: 'NL', name: 'Netherlands', flag: '🇳🇱', dialCode: '+31' },
            { code: 'BE', name: 'Belgium', flag: '🇧🇪', dialCode: '+32' },
            { code: 'CH', name: 'Switzerland', flag: '🇨🇭', dialCode: '+41' },
            { code: 'AT', name: 'Austria', flag: '🇦🇹', dialCode: '+43' },
            { code: 'SE', name: 'Sweden', flag: '🇸🇪', dialCode: '+46' },
            { code: 'NO', name: 'Norway', flag: '🇳🇴', dialCode: '+47' },
            { code: 'DK', name: 'Denmark', flag: '🇩🇰', dialCode: '+45' },
            { code: 'FI', name: 'Finland', flag: '🇫🇮', dialCode: '+358' },
            { code: 'PL', name: 'Poland', flag: '🇵🇱', dialCode: '+48' },
            { code: 'CZ', name: 'Czech Republic', flag: '🇨🇿', dialCode: '+420' },
            { code: 'HU', name: 'Hungary', flag: '🇭🇺', dialCode: '+36' },
            { code: 'PT', name: 'Portugal', flag: '🇵🇹', dialCode: '+351' },
            { code: 'GR', name: 'Greece', flag: '🇬🇷', dialCode: '+30' },
            { code: 'RO', name: 'Romania', flag: '🇷🇴', dialCode: '+40' },
            { code: 'BG', name: 'Bulgaria', flag: '🇧🇬', dialCode: '+359' },
            { code: 'HR', name: 'Croatia', flag: '🇭🇷', dialCode: '+385' },
            { code: 'SI', name: 'Slovenia', flag: '🇸🇮', dialCode: '+386' },
            { code: 'SK', name: 'Slovakia', flag: '🇸🇰', dialCode: '+421' },
            { code: 'LT', name: 'Lithuania', flag: '🇱🇹', dialCode: '+370' },
            { code: 'LV', name: 'Latvia', flag: '🇱🇻', dialCode: '+371' },
            { code: 'EE', name: 'Estonia', flag: '🇪🇪', dialCode: '+372' },
            { code: 'IE', name: 'Ireland', flag: '🇮🇪', dialCode: '+353' },
            { code: 'LU', name: 'Luxembourg', flag: '🇱🇺', dialCode: '+352' },
            { code: 'MT', name: 'Malta', flag: '🇲🇹', dialCode: '+356' },
            { code: 'CY', name: 'Cyprus', flag: '🇨🇾', dialCode: '+357' },
            { code: 'ZA', name: 'South Africa', flag: '🇿🇦', dialCode: '+27' },
            { code: 'NG', name: 'Nigeria', flag: '🇳🇬', dialCode: '+234' },
            { code: 'GH', name: 'Ghana', flag: '🇬🇭', dialCode: '+233' },
            { code: 'EG', name: 'Egypt', flag: '🇪🇬', dialCode: '+20' },
            { code: 'MA', name: 'Morocco', flag: '🇲🇦', dialCode: '+212' },
            { code: 'TN', name: 'Tunisia', flag: '🇹🇳', dialCode: '+216' },
            { code: 'DZ', name: 'Algeria', flag: '🇩🇿', dialCode: '+213' },
            { code: 'LY', name: 'Libya', flag: '🇱🇾', dialCode: '+218' },
            { code: 'SD', name: 'Sudan', flag: '🇸🇩', dialCode: '+249' },
            { code: 'CM', name: 'Cameroon', flag: '🇨🇲', dialCode: '+237' },
            { code: 'CI', name: 'Côte d\'Ivoire', flag: '🇨🇮', dialCode: '+225' },
            { code: 'SN', name: 'Senegal', flag: '🇸🇳', dialCode: '+221' },
            { code: 'ML', name: 'Mali', flag: '🇲🇱', dialCode: '+223' },
            { code: 'BF', name: 'Burkina Faso', flag: '🇧🇫', dialCode: '+226' },
            { code: 'NE', name: 'Niger', flag: '🇳🇪', dialCode: '+227' },
            { code: 'TD', name: 'Chad', flag: '🇹🇩', dialCode: '+235' },
            { code: 'CF', name: 'Central African Republic', flag: '🇨🇫', dialCode: '+236' },
            { code: 'CG', name: 'Congo', flag: '🇨🇬', dialCode: '+242' },
            { code: 'CD', name: 'Democratic Republic of the Congo', flag: '🇨🇩', dialCode: '+243' },
            { code: 'AO', name: 'Angola', flag: '🇦🇴', dialCode: '+244' },
            { code: 'ZM', name: 'Zambia', flag: '🇿🇲', dialCode: '+260' },
            { code: 'ZW', name: 'Zimbabwe', flag: '🇿🇼', dialCode: '+263' },
            { code: 'BW', name: 'Botswana', flag: '🇧🇼', dialCode: '+267' },
            { code: 'NA', name: 'Namibia', flag: '🇳🇦', dialCode: '+264' },
            { code: 'SZ', name: 'Eswatini', flag: '🇸🇿', dialCode: '+268' },
            { code: 'LS', name: 'Lesotho', flag: '🇱🇸', dialCode: '+266' },
            { code: 'MW', name: 'Malawi', flag: '🇲🇼', dialCode: '+265' },
            { code: 'MZ', name: 'Mozambique', flag: '🇲🇿', dialCode: '+258' },
            { code: 'MG', name: 'Madagascar', flag: '🇲🇬', dialCode: '+261' },
            { code: 'MU', name: 'Mauritius', flag: '🇲🇺', dialCode: '+230' },
            { code: 'SC', name: 'Seychelles', flag: '🇸🇨', dialCode: '+248' },
            { code: 'KM', name: 'Comoros', flag: '🇰🇲', dialCode: '+269' },
            { code: 'IN', name: 'India', flag: '🇮🇳', dialCode: '+91' },
            { code: 'PK', name: 'Pakistan', flag: '🇵🇰', dialCode: '+92' },
            { code: 'BD', name: 'Bangladesh', flag: '🇧🇩', dialCode: '+880' },
            { code: 'LK', name: 'Sri Lanka', flag: '🇱🇰', dialCode: '+94' },
            { code: 'NP', name: 'Nepal', flag: '🇳🇵', dialCode: '+977' },
            { code: 'BT', name: 'Bhutan', flag: '🇧🇹', dialCode: '+975' },
            { code: 'MV', name: 'Maldives', flag: '🇲🇻', dialCode: '+960' },
            { code: 'AF', name: 'Afghanistan', flag: '🇦🇫', dialCode: '+93' },
            { code: 'IR', name: 'Iran', flag: '🇮🇷', dialCode: '+98' },
            { code: 'IQ', name: 'Iraq', flag: '🇮🇶', dialCode: '+964' },
            { code: 'TR', name: 'Turkey', flag: '🇹🇷', dialCode: '+90' },
            { code: 'SA', name: 'Saudi Arabia', flag: '🇸🇦', dialCode: '+966' },
            { code: 'AE', name: 'United Arab Emirates', flag: '🇦🇪', dialCode: '+971' },
            { code: 'KW', name: 'Kuwait', flag: '🇰🇼', dialCode: '+965' },
            { code: 'QA', name: 'Qatar', flag: '🇶🇦', dialCode: '+974' },
            { code: 'BH', name: 'Bahrain', flag: '🇧🇭', dialCode: '+973' },
            { code: 'OM', name: 'Oman', flag: '🇴🇲', dialCode: '+968' },
            { code: 'YE', name: 'Yemen', flag: '🇾🇪', dialCode: '+967' },
            { code: 'JO', name: 'Jordan', flag: '🇯🇴', dialCode: '+962' },
            { code: 'LB', name: 'Lebanon', flag: '🇱🇧', dialCode: '+961' },
            { code: 'SY', name: 'Syria', flag: '🇸🇾', dialCode: '+963' },
            { code: 'IL', name: 'Israel', flag: '🇮🇱', dialCode: '+972' },
            { code: 'PS', name: 'Palestine', flag: '🇵🇸', dialCode: '+970' },
            { code: 'CN', name: 'China', flag: '🇨🇳', dialCode: '+86' },
            { code: 'JP', name: 'Japan', flag: '🇯🇵', dialCode: '+81' },
            { code: 'KR', name: 'South Korea', flag: '🇰🇷', dialCode: '+82' },
            { code: 'KP', name: 'North Korea', flag: '🇰🇵', dialCode: '+850' },
            { code: 'TH', name: 'Thailand', flag: '🇹🇭', dialCode: '+66' },
            { code: 'VN', name: 'Vietnam', flag: '🇻🇳', dialCode: '+84' },
            { code: 'MY', name: 'Malaysia', flag: '🇲🇾', dialCode: '+60' },
            { code: 'SG', name: 'Singapore', flag: '🇸🇬', dialCode: '+65' },
            { code: 'ID', name: 'Indonesia', flag: '🇮🇩', dialCode: '+62' },
            { code: 'PH', name: 'Philippines', flag: '🇵🇭', dialCode: '+63' },
            { code: 'BN', name: 'Brunei', flag: '🇧🇳', dialCode: '+673' },
            { code: 'MM', name: 'Myanmar', flag: '🇲🇲', dialCode: '+95' },
            { code: 'KH', name: 'Cambodia', flag: '🇰🇭', dialCode: '+855' },
            { code: 'LA', name: 'Laos', flag: '🇱🇦', dialCode: '+856' },
            { code: 'MN', name: 'Mongolia', flag: '🇲🇳', dialCode: '+976' },
            { code: 'KZ', name: 'Kazakhstan', flag: '🇰🇿', dialCode: '+7' },
            { code: 'UZ', name: 'Uzbekistan', flag: '🇺🇿', dialCode: '+998' },
            { code: 'KG', name: 'Kyrgyzstan', flag: '🇰🇬', dialCode: '+996' },
            { code: 'TJ', name: 'Tajikistan', flag: '🇹🇯', dialCode: '+992' },
            { code: 'TM', name: 'Turkmenistan', flag: '🇹🇲', dialCode: '+993' },
            { code: 'RU', name: 'Russia', flag: '🇷🇺', dialCode: '+7' },
            { code: 'BY', name: 'Belarus', flag: '🇧🇾', dialCode: '+375' },
            { code: 'UA', name: 'Ukraine', flag: '🇺🇦', dialCode: '+380' },
            { code: 'MD', name: 'Moldova', flag: '🇲🇩', dialCode: '+373' },
            { code: 'GE', name: 'Georgia', flag: '🇬🇪', dialCode: '+995' },
            { code: 'AM', name: 'Armenia', flag: '🇦🇲', dialCode: '+374' },
            { code: 'AZ', name: 'Azerbaijan', flag: '🇦🇿', dialCode: '+994' },
            { code: 'BR', name: 'Brazil', flag: '🇧🇷', dialCode: '+55' },
            { code: 'AR', name: 'Argentina', flag: '🇦🇷', dialCode: '+54' },
            { code: 'CL', name: 'Chile', flag: '🇨🇱', dialCode: '+56' },
            { code: 'CO', name: 'Colombia', flag: '🇨🇴', dialCode: '+57' },
            { code: 'PE', name: 'Peru', flag: '🇵🇪', dialCode: '+51' },
            { code: 'VE', name: 'Venezuela', flag: '🇻🇪', dialCode: '+58' },
            { code: 'EC', name: 'Ecuador', flag: '🇪🇨', dialCode: '+593' },
            { code: 'BO', name: 'Bolivia', flag: '🇧🇴', dialCode: '+591' },
            { code: 'PY', name: 'Paraguay', flag: '🇵🇾', dialCode: '+595' },
            { code: 'UY', name: 'Uruguay', flag: '🇺🇾', dialCode: '+598' },
            { code: 'GY', name: 'Guyana', flag: '🇬🇾', dialCode: '+592' },
            { code: 'SR', name: 'Suriname', flag: '🇸🇷', dialCode: '+597' },
            { code: 'GF', name: 'French Guiana', flag: '🇬🇫', dialCode: '+594' },
            { code: 'MX', name: 'Mexico', flag: '🇲🇽', dialCode: '+52' },
            { code: 'GT', name: 'Guatemala', flag: '🇬🇹', dialCode: '+502' },
            { code: 'BZ', name: 'Belize', flag: '🇧🇿', dialCode: '+501' },
            { code: 'SV', name: 'El Salvador', flag: '🇸🇻', dialCode: '+503' },
            { code: 'HN', name: 'Honduras', flag: '🇭🇳', dialCode: '+504' },
            { code: 'NI', name: 'Nicaragua', flag: '🇳🇮', dialCode: '+505' },
            { code: 'CR', name: 'Costa Rica', flag: '🇨🇷', dialCode: '+506' },
            { code: 'PA', name: 'Panama', flag: '🇵🇦', dialCode: '+507' },
            { code: 'CU', name: 'Cuba', flag: '🇨🇺', dialCode: '+53' },
            { code: 'JM', name: 'Jamaica', flag: '🇯🇲', dialCode: '+1876' },
            { code: 'HT', name: 'Haiti', flag: '🇭🇹', dialCode: '+509' },
            { code: 'DO', name: 'Dominican Republic', flag: '🇩🇴', dialCode: '+1809' },
            { code: 'TT', name: 'Trinidad and Tobago', flag: '🇹🇹', dialCode: '+1868' },
            { code: 'BB', name: 'Barbados', flag: '🇧🇧', dialCode: '+1246' },
            { code: 'AG', name: 'Antigua and Barbuda', flag: '🇦🇬', dialCode: '+1268' },
            { code: 'DM', name: 'Dominica', flag: '🇩🇲', dialCode: '+1767' },
            { code: 'GD', name: 'Grenada', flag: '🇬🇩', dialCode: '+1473' },
            { code: 'KN', name: 'Saint Kitts and Nevis', flag: '🇰🇳', dialCode: '+1869' },
            { code: 'LC', name: 'Saint Lucia', flag: '🇱🇨', dialCode: '+1758' },
            { code: 'VC', name: 'Saint Vincent and the Grenadines', flag: '🇻🇨', dialCode: '+1784' },
            { code: 'BS', name: 'Bahamas', flag: '🇧🇸', dialCode: '+1242' }
        ];
        
        this.selectedCountry = this.countries.find(c => c.code === this.options.defaultCountry);
        this.init();
    }
    
    init() {
        // Check if already initialized
        if (this.container.querySelector('.country-code-selector')) {
            console.warn(`Country code selector already initialized for ${this.container.id}`);
            return;
        }
        
        this.createHTML();
        this.bindEvents();
    }
    
    createHTML() {
        // Generate unique IDs for this selector instance
        const uniqueId = this.container.id + '-';
        const selectedCountryId = uniqueId + 'selected-country';
        const countryOptionsId = uniqueId + 'country-options';
        const countrySearchInputId = uniqueId + 'country-search-input';
        const countryListId = uniqueId + 'country-list';
        const phoneNumberId = uniqueId + 'phone-number';
        
        this.container.innerHTML = `
            <div class="country-code-selector">
                <div class="country-code-dropdown">
                    <div class="country-code-selected" id="${selectedCountryId}">
                        <span class="country-flag">${this.selectedCountry.flag}</span>
                        <span class="country-dial-code">${this.selectedCountry.dialCode}</span>
                        <i class="fas fa-chevron-down dropdown-arrow"></i>
                    </div>
                    <div class="country-code-options" id="${countryOptionsId}">
                        ${this.options.searchEnabled ? `
                            <div class="country-search">
                                <input type="text" placeholder="Search countries..." id="${countrySearchInputId}">
                                <i class="fas fa-search search-icon"></i>
                            </div>
                        ` : ''}
                        <div class="country-list" id="${countryListId}">
                            ${this.renderCountryList()}
                        </div>
                    </div>
                </div>
                <input type="tel" class="phone-number-input" id="${phoneNumberId}" placeholder="Phone number">
            </div>
        `;
        
        this.selectedElement = document.getElementById(selectedCountryId);
        this.optionsElement = document.getElementById(countryOptionsId);
        this.phoneInput = document.getElementById(phoneNumberId);
        this.countryList = document.getElementById(countryListId);
        
        // Debug: Check if elements were found
        if (!this.phoneInput) {
            console.error(`Phone input element not found in selector. Looking for ID: ${phoneNumberId}`);
        }
        if (!this.selectedElement) {
            console.error(`Selected element not found in selector. Looking for ID: ${selectedCountryId}`);
        }
        
        // Set initial placeholder
        this.updatePlaceholder();
    }
    
    renderCountryList() {
        return this.countries.map(country => `
            <div class="country-option" data-code="${country.code}" data-dial-code="${country.dialCode}">
                <span class="country-flag">${country.flag}</span>
                <span class="country-name">${country.name}</span>
                <span class="country-dial-code">${country.dialCode}</span>
            </div>
        `).join('');
    }
    
    bindEvents() {
        // Store bound functions for cleanup
        this.boundToggleDropdown = (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        };
        
        this.boundHandleCountrySelection = (e) => {
            e.stopPropagation();
            const countryOption = e.target.closest('.country-option');
            if (countryOption) {
                this.selectCountry(countryOption.dataset.code);
                this.closeDropdown();
            }
        };
        
        this.boundFormatPhone = (e) => {
            this.formatPhoneNumber(e.target.value);
        };
        
        this.boundHandleKeydown = (e) => {
            this.handleKeydown(e);
        };
        
        this.boundHandlePaste = (e) => {
            this.handlePaste(e);
        };
        
        this.boundCloseOnOutsideClick = (e) => {
            if (!this.container.contains(e.target)) {
                this.closeDropdown();
            }
        };
        
        this.boundPreventClose = (e) => {
            e.stopPropagation();
        };
        
        // Toggle dropdown
        this.selectedElement.addEventListener('click', this.boundToggleDropdown);
        
        // Country selection
        this.countryList.addEventListener('click', this.boundHandleCountrySelection);
        
        // Search functionality
        if (this.options.searchEnabled) {
            const searchInputId = this.container.id + '-country-search-input';
            const searchInput = document.getElementById(searchInputId);
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    e.stopPropagation();
                    this.filterCountries(e.target.value);
                });
                
                searchInput.addEventListener('click', (e) => {
                    e.stopPropagation();
                });
            }
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', this.boundCloseOnOutsideClick);
        
        // Phone number formatting and guidance with better event handling
        this.phoneInput.addEventListener('input', this.boundFormatPhone);
        this.phoneInput.addEventListener('keydown', this.boundHandleKeydown);
        this.phoneInput.addEventListener('paste', this.boundHandlePaste);
        
        // Prevent dropdown from closing when clicking inside options
        this.optionsElement.addEventListener('click', this.boundPreventClose);
    }
    
    toggleDropdown() {
        this.optionsElement.classList.toggle('show');
    }
    
    closeDropdown() {
        this.optionsElement.classList.remove('show');
    }
    
    selectCountry(countryCode) {
        this.selectedCountry = this.countries.find(c => c.code === countryCode);
        this.selectedElement.innerHTML = `
            <span class="country-flag">${this.selectedCountry.flag}</span>
            <span class="country-dial-code">${this.selectedCountry.dialCode}</span>
            <i class="fas fa-chevron-down dropdown-arrow"></i>
        `;
        
        // Update placeholder for new country
        this.updatePlaceholder();
        
        // Reformat current phone number for new country
        const currentValue = this.phoneInput.value;
        if (currentValue) {
            this.formatPhoneNumber(currentValue);
        }
        
        // Trigger change event
        this.container.dispatchEvent(new CustomEvent('countryChanged', {
            detail: {
                country: this.selectedCountry,
                fullPhoneNumber: this.getFullPhoneNumber()
            }
        }));
    }
    
    filterCountries(searchTerm) {
        const filteredCountries = this.countries.filter(country =>
            country.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            country.dialCode.includes(searchTerm)
        );
        
        this.countryList.innerHTML = filteredCountries.map(country => `
            <div class="country-option" data-code="${country.code}" data-dial-code="${country.dialCode}">
                <span class="country-flag">${country.flag}</span>
                <span class="country-name">${country.name}</span>
                <span class="country-dial-code">${country.dialCode}</span>
            </div>
        `).join('');
    }
    
    formatPhoneNumber(value) {
        // Store cursor position before formatting
        const cursorPosition = this.phoneInput.selectionStart;
        
        // Remove all non-numeric characters except + at the beginning
        let cleanValue = value.replace(/[^\d]/g, '');
        
        // Handle common prefixes like 07, 0, etc.
        cleanValue = this.cleanPhoneNumber(cleanValue);
        
        // Only format if the value has changed significantly to avoid cursor jumping
        const currentFormatted = this.phoneInput.value;
        const currentClean = currentFormatted.replace(/[^\d]/g, '');
        
        // Don't reformat if user is just deleting and values are similar
        if (cleanValue === currentClean && Math.abs(cleanValue.length - currentClean.length) <= 1) {
            return;
        }
        
        // Format based on country
        let formatted = cleanValue;
        if (this.selectedCountry.code === 'UG') {
            // Ugandan format: 700 123 456
            if (cleanValue.length > 6) {
                formatted = cleanValue.substring(0, 3) + ' ' + cleanValue.substring(3, 6) + ' ' + cleanValue.substring(6, 9);
            } else if (cleanValue.length > 3) {
                formatted = cleanValue.substring(0, 3) + ' ' + cleanValue.substring(3, 6);
            }
        } else if (this.selectedCountry.code === 'KE') {
            // Kenyan format: 700 123 456
            if (cleanValue.length > 6) {
                formatted = cleanValue.substring(0, 3) + ' ' + cleanValue.substring(3, 6) + ' ' + cleanValue.substring(6, 9);
            } else if (cleanValue.length > 3) {
                formatted = cleanValue.substring(0, 3) + ' ' + cleanValue.substring(3, 6);
            }
        } else if (this.selectedCountry.code === 'US' || this.selectedCountry.code === 'CA') {
            // US/Canada format: (555) 123-4567
            if (cleanValue.length >= 10) {
                formatted = `(${cleanValue.substring(0, 3)}) ${cleanValue.substring(3, 6)}-${cleanValue.substring(6, 10)}`;
            } else if (cleanValue.length >= 6) {
                formatted = `(${cleanValue.substring(0, 3)}) ${cleanValue.substring(3, 6)}-${cleanValue.substring(6)}`;
            } else if (cleanValue.length >= 3) {
                formatted = `(${cleanValue.substring(0, 3)}) ${cleanValue.substring(3)}`;
            }
        }
        
        // Only update if the formatted value is different
        if (formatted !== currentFormatted) {
            this.phoneInput.value = formatted;
            
            // Restore cursor position after formatting
            setTimeout(() => {
                this.restoreCursorPosition(cursorPosition, currentFormatted, formatted);
            }, 0);
        }
        
        // Update placeholder based on country
        this.updatePlaceholder();
        
        // Trigger change event
        this.container.dispatchEvent(new CustomEvent('phoneChanged', {
            detail: {
                fullPhoneNumber: this.getFullPhoneNumber(),
                country: this.selectedCountry
            }
        }));
    }
    
    restoreCursorPosition(originalPosition, oldValue, newValue) {
        // Calculate the new cursor position based on the formatting changes
        let newPosition = originalPosition;
        
        // If the new value is longer (spaces added), adjust cursor position
        const lengthDiff = newValue.length - oldValue.length;
        if (lengthDiff > 0) {
            // Count spaces before the cursor position in the new value
            let spacesBeforeCursor = 0;
            for (let i = 0; i < Math.min(newPosition, newValue.length); i++) {
                if (newValue[i] === ' ' || newValue[i] === '(' || newValue[i] === ')' || newValue[i] === '-') {
                    spacesBeforeCursor++;
                }
            }
            newPosition += spacesBeforeCursor;
        }
        
        // Ensure cursor position is within bounds
        newPosition = Math.min(newPosition, newValue.length);
        
        this.phoneInput.setSelectionRange(newPosition, newPosition);
    }
    
    handleKeydown(e) {
        // Allow backspace, delete, arrow keys, and other navigation keys
        const allowedKeys = [
            'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Home', 'End', 'Tab', 'Enter', 'Escape'
        ];
        
        // Allow Ctrl/Cmd combinations
        if (e.ctrlKey || e.metaKey) {
            return;
        }
        
        // Allow allowed keys
        if (allowedKeys.includes(e.key)) {
            return;
        }
        
        // Allow numbers
        if (e.key >= '0' && e.key <= '9') {
            return;
        }
        
        // Block other keys
        e.preventDefault();
    }
    
    handlePaste(e) {
        // Handle paste events to clean the input
        e.preventDefault();
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');
        const cleanedText = pastedText.replace(/[^\d]/g, '');
        
        // Insert the cleaned text at cursor position
        const start = this.phoneInput.selectionStart;
        const end = this.phoneInput.selectionEnd;
        const currentValue = this.phoneInput.value;
        const newValue = currentValue.substring(0, start) + cleanedText + currentValue.substring(end);
        
        this.phoneInput.value = newValue;
        
        // Format the new value
        this.formatPhoneNumber(newValue);
        
        // Set cursor position after the pasted text
        const newCursorPosition = start + cleanedText.length;
        setTimeout(() => {
            this.phoneInput.setSelectionRange(newCursorPosition, newCursorPosition);
        }, 0);
    }
    
    cleanPhoneNumber(value) {
        // Remove leading zeros and common prefixes
        if (value.startsWith('0')) {
            value = value.substring(1);
        }
        
        // Handle specific country codes that might be entered without country code
        if (this.selectedCountry.code === 'UG') {
            // If user enters 256 at the beginning, remove it since we'll add it
            if (value.startsWith('256')) {
                value = value.substring(3);
            }
        } else if (this.selectedCountry.code === 'KE') {
            // If user enters 254 at the beginning, remove it since we'll add it
            if (value.startsWith('254')) {
                value = value.substring(3);
            }
        }
        
        return value;
    }
    
    updatePlaceholder() {
        let placeholder = '';
        if (this.selectedCountry.code === 'UG') {
            placeholder = '700 123 456 (without 0 or +256)';
        } else if (this.selectedCountry.code === 'KE') {
            placeholder = '700 123 456 (without 0 or +254)';
        } else if (this.selectedCountry.code === 'US' || this.selectedCountry.code === 'CA') {
            placeholder = '555 123 4567 (without +1)';
        } else {
            placeholder = 'Phone number (without country code)';
        }
        
        this.phoneInput.placeholder = placeholder;
    }
    
    getFullPhoneNumber() {
        if (!this.phoneInput) {
            console.error('Phone input not found in selector');
            return '';
        }
        const phoneNumber = this.phoneInput.value.replace(/\D/g, '');
        return phoneNumber ? `${this.selectedCountry.dialCode}${phoneNumber}` : '';
    }
    
    getValue() {
        return this.getFullPhoneNumber();
    }
    
    setValue(phoneNumber) {
        // Extract country code and number from full phone number
        if (phoneNumber) {
            const country = this.countries.find(c => phoneNumber.startsWith(c.dialCode));
            if (country) {
                this.selectCountry(country.code);
                const number = phoneNumber.substring(country.dialCode.length);
                this.phoneInput.value = number;
            }
        }
    }
    
    validate() {
        const fullNumber = this.getFullPhoneNumber();
        const phoneNumber = this.phoneInput.value.replace(/\D/g, '');
        
        // Basic validation - must have at least 7 digits after country code
        if (!fullNumber || fullNumber.length < 8) {
            return false;
        }
        
        // Check if phone number part is reasonable length
        if (phoneNumber.length < 7 || phoneNumber.length > 15) {
            return false;
        }
        
        // Country-specific validation
        if (this.selectedCountry.code === 'UG' || this.selectedCountry.code === 'KE') {
            // East African numbers should be 9 digits after country code
            return phoneNumber.length === 9 && phoneNumber.startsWith('7');
        }
        
        // General international validation
        const phoneRegex = /^\+\d{7,15}$/;
        return phoneRegex.test(fullNumber);
    }
    
    getValidationMessage() {
        const phoneNumber = this.phoneInput.value.replace(/\D/g, '');
        
        if (!phoneNumber) {
            return 'Please enter a phone number';
        }
        
        if (this.selectedCountry.code === 'UG' || this.selectedCountry.code === 'KE') {
            if (phoneNumber.length !== 9) {
                return 'Phone number must be 9 digits (e.g., 700123456)';
            }
            if (!phoneNumber.startsWith('7')) {
                return 'Phone number should start with 7 (e.g., 700123456)';
            }
        }
        
        if (phoneNumber.length < 7 || phoneNumber.length > 15) {
            return 'Phone number must be between 7-15 digits';
        }
        
        return 'Valid phone number';
    }
    
    destroy() {
        // Remove event listeners
        if (this.selectedElement && this.boundToggleDropdown) {
            this.selectedElement.removeEventListener('click', this.boundToggleDropdown);
        }
        
        if (this.countryList && this.boundHandleCountrySelection) {
            this.countryList.removeEventListener('click', this.boundHandleCountrySelection);
        }
        
        if (this.phoneInput && this.boundFormatPhone) {
            this.phoneInput.removeEventListener('input', this.boundFormatPhone);
        }
        
        if (this.phoneInput && this.boundHandleKeydown) {
            this.phoneInput.removeEventListener('keydown', this.boundHandleKeydown);
        }
        
        if (this.phoneInput && this.boundHandlePaste) {
            this.phoneInput.removeEventListener('paste', this.boundHandlePaste);
        }
        
        if (this.optionsElement && this.boundPreventClose) {
            this.optionsElement.removeEventListener('click', this.boundPreventClose);
        }
        
        if (this.boundCloseOnOutsideClick) {
            document.removeEventListener('click', this.boundCloseOnOutsideClick);
        }
        
        // Clear the container
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// CSS Styles
const countryCodeStyles = `
<style>
.country-code-selector {
    display: flex;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    background: white;
    transition: border-color 0.3s ease;
}

.country-code-selector:focus-within {
    border-color: #008080;
    box-shadow: 0 0 0 3px rgba(0, 128, 128, 0.1);
}

.country-code-dropdown {
    position: relative;
    min-width: 120px;
}

.country-code-selected {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    cursor: pointer;
    background: #f9fafb;
    border-radius: 6px 0 0 6px;
    border-right: 1px solid #e5e7eb;
    transition: background-color 0.3s ease;
}

.country-code-selected:hover {
    background: #f3f4f6;
}

.country-flag {
    font-size: 18px;
    margin-right: 8px;
}

.country-dial-code {
    font-weight: 600;
    color: #374151;
    margin-right: 8px;
}

.dropdown-arrow {
    color: #6b7280;
    font-size: 12px;
    transition: transform 0.3s ease;
}

.country-code-options {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    max-height: 300px;
    overflow: hidden;
    display: none;
}

.country-code-options.show {
    display: block;
}

.country-search {
    position: relative;
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
}

.country-search input {
    width: 100%;
    padding: 8px 12px 8px 40px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    font-size: 14px;
    outline: none;
}

.country-search input:focus {
    border-color: #008080;
    box-shadow: 0 0 0 3px rgba(0, 128, 128, 0.1);
}

.search-icon {
    position: absolute;
    left: 24px;
    top: 50%;
    transform: translateY(-50%);
    color: #6b7280;
    font-size: 14px;
}

.country-list {
    max-height: 240px;
    overflow-y: auto;
}

.country-option {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    cursor: pointer;
    transition: background-color 0.2s ease;
    border-bottom: 1px solid #f3f4f6;
}

.country-option:hover {
    background: #f9fafb;
}

.country-option:last-child {
    border-bottom: none;
}

.country-option .country-name {
    flex: 1;
    margin-left: 8px;
    font-size: 14px;
    color: #374151;
}

.country-option .country-dial-code {
    font-weight: 600;
    color: #008080;
    font-size: 14px;
}

.phone-number-input {
    flex: 1;
    padding: 12px 16px;
    border: none;
    outline: none;
    font-size: 16px;
    border-radius: 0 6px 6px 0;
}

.phone-number-input::placeholder {
    color: #9ca3af;
}

/* Responsive design */
@media (max-width: 640px) {
    .country-code-selector {
        flex-direction: column;
    }
    
    .country-code-dropdown {
        min-width: 100%;
    }
    
    .country-code-selected {
        border-radius: 6px 6px 0 0;
        border-right: none;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .phone-number-input {
        border-radius: 0 0 6px 6px;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', countryCodeStyles);

// Country Code Selector Manager
class CountryCodeManager {
    constructor() {
        this.selectors = new Map();
    }
    
    create(containerId, options = {}) {
        console.log(`Creating country code selector for: ${containerId}`); // Debug log
        
        // Clean up existing selector if it exists
        this.destroy(containerId);
        
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container with ID '${containerId}' not found`);
            console.error('Available containers:', document.querySelectorAll('[id*="PhoneSelector"]')); // Debug log
            return null;
        }
        
        console.log(`Container found for ${containerId}:`, container); // Debug log
        
        try {
            const selector = new CountryCodeSelector(containerId, options);
            this.selectors.set(containerId, selector);
            console.log(`Successfully created selector for ${containerId}:`, selector); // Debug log
            return selector;
        } catch (error) {
            console.error(`Error creating selector for ${containerId}:`, error);
            return null;
        }
    }
    
    get(containerId) {
        return this.selectors.get(containerId);
    }
    
    destroy(containerId) {
        const selector = this.selectors.get(containerId);
        if (selector) {
            // Call the selector's destroy method
            if (typeof selector.destroy === 'function') {
                selector.destroy();
            }
            this.selectors.delete(containerId);
        }
    }
    
    destroyAll() {
        for (const containerId of this.selectors.keys()) {
            this.destroy(containerId);
        }
    }
}

// Global manager instance
window.countryCodeManager = new CountryCodeManager();

// Make it globally available
window.CountryCodeSelector = CountryCodeSelector;
