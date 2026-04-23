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
