
/**
 * OneXportal Toolkit — Dynamic Command Renderer
 * Loads command data from JSON and renders it dynamically
 */

class ToolkitRenderer {
    constructor(dataUrl, options = {}) {
        this.dataUrl = dataUrl;
        this.data = null;
        this.options = {
            mainContentId: 'mainContent',
            sidebarNavId: 'sidebarNav',
            categoryMenuCurrentId: 'categoryMenuCurrent',
            searchInputId: 'searchInput',
            categoryMenuSearchId: 'categoryMenuSearch',
            categoryMenuTriggerId: 'categoryMenuTrigger',
            categoryMenuPanelId: 'categoryMenuPanel',
            ...options
        };
    }

    /**
     * Initialize: Load JSON and set up event listeners
     */
    async init() {
        try {
            await this.loadData();
            this.renderCategories();
            this.setupEventListeners();
            this.updateCommandCount();
        } catch (error) {
            console.error('Failed to initialize toolkit:', error);
        }
    }

    /**
     * Load command data from JSON file
     */
    async loadData() {
        const response = await fetch(this.dataUrl);
        if (!response.ok) throw new Error(`Failed to load ${this.dataUrl}`);
        this.data = await response.json();
    }

    /**
     * Create or update the debug panel used for clipboard diagnostics
     */
    createDebugPanel() {
        let debugPanel = document.getElementById('clipboardDebugPanel');
        if (!debugPanel) {
            debugPanel = document.createElement('div');
            debugPanel.id = 'clipboardDebugPanel';
            debugPanel.className = 'clipboard-debug-panel';
            debugPanel.style.position = 'fixed';
            debugPanel.style.bottom = '1rem';
            debugPanel.style.right = '1rem';
            debugPanel.style.padding = '0.75rem 1rem';
            debugPanel.style.background = 'rgba(0,0,0,0.8)';
            debugPanel.style.color = '#fff';
            debugPanel.style.fontSize = '0.85rem';
            debugPanel.style.borderRadius = '0.5rem';
            debugPanel.style.maxWidth = '320px';
            debugPanel.style.zIndex = '9999';
            debugPanel.style.boxShadow = '0 12px 30px rgba(0,0,0,0.25)';
            debugPanel.textContent = 'Clipboard debug panel ready.';
            document.body.appendChild(debugPanel);
        }
        return debugPanel;
    }

    /**
     * Update the clipboard debug panel text
     */
    updateDebugPanel(message) {
        const debugPanel = this.createDebugPanel();
        debugPanel.textContent = message;
    }

    /**
     * Render all categories and their commands
     */
    renderCategories() {
        const mainContent = document.getElementById(this.options.mainContentId);
        mainContent.innerHTML = '';

        this.data.categories.forEach(category => {
            const section = this.createCategorySection(category);
            mainContent.appendChild(section);
        });
    }

    /**
     * Create a category section with command cards
     */
    createCategorySection(category) {
        const section = document.createElement('section');
        section.id = category.id;
        section.setAttribute('data-cat-id', category.id);
        section.className = 'category-section';

        // Header
        const h2 = document.createElement('h2');
        h2.innerHTML = `<i class="${category.icon}"></i> ${this.escapeHtml(category.title)}`;
        section.appendChild(h2);

        // Description
        const desc = document.createElement('p');
        desc.className = 'cat-desc';
        desc.textContent = category.description;
        section.appendChild(desc);

        // Commands grid
        const grid = document.createElement('div');
        grid.className = 'cards-grid';

        category.commands.forEach(cmd => {
            grid.appendChild(this.createCommandCard(cmd));
        });

        section.appendChild(grid);
        return section;
    }

    /**
     * Create a single command card
     */
    createCommandCard(cmd) {
        const card = document.createElement('article');
        card.id = `cmd-${cmd.id}`;
        card.className = 'command-card';

        // Header with title and badge
        const header = document.createElement('div');
        header.className = 'card-header';

        const h3 = document.createElement('h3');
        h3.textContent = cmd.title;
        header.appendChild(h3);

        if (cmd.isDanger) {
            const badge = document.createElement('span');
            badge.className = 'danger-badge';
            badge.textContent = 'Danger';
            header.appendChild(badge);
        }

        card.appendChild(header);

        // Code block
        const codeBlock = document.createElement('div');
        codeBlock.className = 'code-block';

        const pre = document.createElement('pre');
        const code = document.createElement('code');
        code.textContent = cmd.command || cmd.code || '';
        code.id = `code-${cmd.id}`;
        pre.appendChild(code);
        codeBlock.appendChild(pre);

        // Code actions (copy, edit)
        const actions = document.createElement('div');
        actions.className = 'code-actions';

        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.textContent = 'Copy';
        copyBtn.onclick = () => this.copyToClipboard(code, copyBtn);
        actions.appendChild(copyBtn);

        const editBtn = document.createElement('button');
        editBtn.className = 'edit-btn';
        editBtn.textContent = 'Edit';
        editBtn.onclick = () => this.toggleEdit(code, editBtn);
        actions.appendChild(editBtn);

        codeBlock.appendChild(actions);
        card.appendChild(codeBlock);

        // Description
        if (cmd.description) {
            const desc = document.createElement('p');
            desc.className = 'description';
            desc.textContent = cmd.description;
            card.appendChild(desc);
        }

        // How to use
        if (cmd.howToUse) {
            const howTo = document.createElement('div');
            howTo.className = 'how-to-use';
            const label = document.createElement('span');
            label.className = 'label';
            label.textContent = 'How to use';
            howTo.appendChild(label);
            const p = document.createElement('p');
            p.innerHTML = cmd.howToUse.replace(/\n/g, '<br>');
            howTo.appendChild(p);
            card.appendChild(howTo);
        }

        // Tip box
        if (cmd.tip) {
            const tipBox = document.createElement('div');
            tipBox.className = 'tip-box';
            const p = document.createElement('p');
            p.innerHTML = cmd.tip.replace(/\n/g, '<br>');
            tipBox.appendChild(p);
            card.appendChild(tipBox);
        }

        // When to use
        if (cmd.whenToUse) {
            const whenTo = document.createElement('div');
            whenTo.className = 'when-to-use';
            const label = document.createElement('span');
            label.className = 'label';
            label.textContent = 'When to use';
            whenTo.appendChild(label);
            const p = document.createElement('p');
            p.textContent = cmd.whenToUse;
            whenTo.appendChild(p);
            card.appendChild(whenTo);
        }

        return card;
    }

    /**
     * Render sidebar navigation
     */
    renderSidebar() {
        const sidebarNav = document.getElementById(this.options.sidebarNavId);
        sidebarNav.innerHTML = '';

        if (this.data.categories.length === 1) {
            const category = this.data.categories[0];
            category.commands.forEach(cmd => {
                const link = document.createElement('a');
                link.href = `#cmd-${cmd.id}`;
                link.className = 'cat-link';
                link.setAttribute('data-cat', `cmd-${cmd.id}`);
                link.setAttribute('role', 'menuitem');
                link.textContent = cmd.title;
                link.addEventListener('click', () => this.selectCategory(`cmd-${cmd.id}`));
                sidebarNav.appendChild(link);
            });
            return;
        }

        this.data.categories.forEach(category => {
            const link = document.createElement('a');
            link.href = `#${category.id}`;
            link.className = 'cat-link';
            link.setAttribute('data-cat', category.id);
            link.setAttribute('role', 'menuitem');

            const icon = document.createElement('i');
            icon.className = category.icon;
            link.appendChild(icon);

            const span = document.createElement('span');
            span.textContent = category.title;
            link.appendChild(span);

            link.addEventListener('click', () => this.selectCategory(category.id));

            sidebarNav.appendChild(link);
        });
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Render sidebar
        this.renderSidebar();

        // Search input
        const searchInput = document.getElementById(this.options.searchInputId);
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Category menu search
        const catMenuSearch = document.getElementById(this.options.categoryMenuSearchId);
        if (catMenuSearch) {
            catMenuSearch.addEventListener('input', (e) => this.handleCategoryMenuSearch(e.target.value));
        }

        // Category menu trigger
        const trigger = document.getElementById(this.options.categoryMenuTriggerId);
        if (trigger) {
            trigger.addEventListener('click', () => this.toggleCategoryMenu());
        }

        // Category links click handler
        document.addEventListener('click', (e) => {
            if (e.target.closest('.cat-link')) {
                const catId = e.target.closest('.cat-link').getAttribute('data-cat');
                this.selectCategory(catId);
            }
        });
    }

    /**
     * Handle global search
     */
    handleSearch(query) {
        const cards = document.querySelectorAll('.command-card');
        const lowerQuery = query.toLowerCase();

        cards.forEach(card => {
            const text = card.innerText.toLowerCase();
            card.style.display = text.includes(lowerQuery) ? '' : 'none';
        });
    }

    /**
     * Handle category menu search
     */
    handleCategoryMenuSearch(query) {
        const links = document.querySelectorAll('.cat-link');
        const lowerQuery = query.toLowerCase();

        links.forEach(link => {
            const text = link.innerText.toLowerCase();
            link.hidden = !text.includes(lowerQuery);
        });
    }

    /**
     * Toggle category menu
     */
    toggleCategoryMenu() {
        const panel = document.getElementById(this.options.categoryMenuPanelId);
        const trigger = document.getElementById(this.options.categoryMenuTriggerId);

        if (panel.hidden) {
            panel.hidden = false;
            trigger.setAttribute('aria-expanded', 'true');
        } else {
            panel.hidden = true;
            trigger.setAttribute('aria-expanded', 'false');
        }
    }

    /**
     * Select and highlight a category
     */
    selectCategory(catId) {
        // Remove active class from all links
        document.querySelectorAll('.cat-link').forEach(link => {
            link.classList.remove('active');
        });

        const selectedLink = document.querySelector(`[data-cat="${catId}"]`);
        if (selectedLink) {
            selectedLink.classList.add('active');
        }

        const category = this.data.categories.find(c => c.id === catId);
        const current = document.getElementById(this.options.categoryMenuCurrentId);

        if (category) {
            if (current) {
                current.textContent = category.title;
            }
            const section = document.getElementById(catId);
            if (section) {
                section.scrollIntoView({ behavior: 'smooth' });
            }
        } else {
            const command = this.data.categories.reduce((found, cat) => found || cat.commands.find(cmd => `cmd-${cmd.id}` === catId), null);
            if (command) {
                if (current) {
                    current.textContent = command.title;
                }
                const commandEl = document.getElementById(catId);
                if (commandEl) {
                    commandEl.scrollIntoView({ behavior: 'smooth' });
                }
            }
        }

        // Close menu on mobile
        const panel = document.getElementById(this.options.categoryMenuPanelId);
        const trigger = document.getElementById(this.options.categoryMenuTriggerId);
        if (panel && !panel.hidden) {
            panel.hidden = true;
            trigger.setAttribute('aria-expanded', 'false');
        }
    }

    /**
     * Copy code to clipboard
     */
    async copyToClipboard(codeElement, button) {
        try {
            const text = codeElement.textContent;
            await navigator.clipboard.writeText(text);

            button.classList.add('copied');
            button.textContent = 'Copied!';
            this.updateDebugPanel('Copied command');

            setTimeout(() => {
                button.classList.remove('copied');
                button.textContent = 'Copy';
            }, 2000);
        } catch (error) {
            console.error('Failed to copy:', error);
            button.textContent = 'Failed';
            this.updateDebugPanel(`Copy failed: ${error.message}`);
        }
    }

    /**
     * Toggle inline editing
     */
    toggleEdit(codeElement, button) {
        if (codeElement.contentEditable === 'true') {
            codeElement.contentEditable = 'false';
            button.classList.remove('active');
            button.textContent = 'Edit';
        } else {
            codeElement.contentEditable = 'true';
            codeElement.focus();
            button.classList.add('active');
            button.textContent = 'Done';
        }
    }

    /**
     * Update command count in hero section
     */
    updateCommandCount() {
        const count = this.data.categories.reduce((sum, cat) => sum + cat.commands.length, 0);
        const total = this.data.metadata.commandCount || count;

        // Update all command count displays
        const countElements = document.querySelectorAll('[data-command-count]');
        countElements.forEach(el => {
            el.textContent = total;
        });

        // Update brand subtitle
        const brandSub = document.querySelector('.brand-sub');
        if (brandSub) {
            brandSub.textContent = `${total} commands · Click to copy · Edit to change placeholders`;
        }
    }

    /**
     * Utility: Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

/**
 * Auto-initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    // Detect which data file to load based on current page
    const isGitPage = document.title.includes('Git');
    const dataUrl = isGitPage
        ? 'assets/data/commands-git.json'
        : 'assets/data/commands-termux.json';

    const renderer = new ToolkitRenderer(dataUrl);
    renderer.init();
});
