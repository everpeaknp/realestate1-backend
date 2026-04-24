// Enhanced CKEditor Fullscreen Functionality
(function() {
    'use strict';
    
    // Wait for CKEditor to be ready
    if (typeof CKEDITOR !== 'undefined') {
        CKEDITOR.on('instanceReady', function(evt) {
            var editor = evt.editor;
            
            // Add keyboard shortcut for fullscreen (F11 or Ctrl+Shift+F)
            editor.on('key', function(e) {
                // F11 key
                if (e.data.keyCode === 122) {
                    e.cancel();
                    editor.execCommand('maximize');
                }
                // Ctrl+Shift+F
                if (e.data.domEvent.$.ctrlKey && e.data.domEvent.$.shiftKey && e.data.keyCode === 70) {
                    e.cancel();
                    editor.execCommand('maximize');
                }
            });
            
            // Add tooltip to maximize button
            var maximizeButton = editor.ui.get('Maximize');
            if (maximizeButton) {
                maximizeButton.label = 'Fullscreen (F11 or Ctrl+Shift+F)';
            }
            
            // Add notification when entering/exiting fullscreen
            editor.on('maximize', function(e) {
                if (e.data === CKEDITOR.TRISTATE_ON) {
                    console.log('Entered fullscreen mode. Press F11 or click Maximize button to exit.');
                } else {
                    console.log('Exited fullscreen mode.');
                }
            });
        });
    }
})();

// Prevent auto-scroll to top when clicking sidebar menu items
(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        // Find all sidebar menu links
        var sidebarLinks = document.querySelectorAll('.sidebar-menu a, .nav-sidebar a');
        
        sidebarLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                // Only prevent scroll if it's a collapsible menu item (has submenu)
                if (this.classList.contains('has-treeview') || this.getAttribute('data-toggle') === 'collapse') {
                    // Store current scroll position
                    var scrollPos = window.pageYOffset || document.documentElement.scrollTop;
                    
                    // After a short delay, restore scroll position
                    setTimeout(function() {
                        window.scrollTo(0, scrollPos);
                    }, 10);
                }
            });
        });
        
        // Prevent Jazzmin's default scroll behavior
        var style = document.createElement('style');
        style.textContent = `
            html {
                scroll-behavior: auto !important;
            }
        `;
        document.head.appendChild(style);
    });
})();
