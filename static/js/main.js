// Document Ready Event
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the appropriate page based on the current URL
    // const currentPath = window.location.pathname;

        initQueryPage();
        
        // Add event listeners for sidebar menu items
        const sidebarMenuItems = document.querySelectorAll('.sidebar-menu li');
        sidebarMenuItems.forEach(item => {
            item.addEventListener('click', function() {
                // Remove active class from all items
                sidebarMenuItems.forEach(i => i.classList.remove('active'));
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Get the section to show
                const sectionId = this.getAttribute('data-section');
                
                // Hide all sections
                const sections = document.querySelectorAll('.content-section');
                sections.forEach(section => section.classList.remove('active'));
                
                // Show the selected section
                const selectedSection = document.getElementById(sectionId);
                if (selectedSection) {
                    selectedSection.classList.add('active');
                }
                
                // Update the section title
                const sectionTitle = document.getElementById('section-title');
                if (sectionTitle) {
                    sectionTitle.textContent = this.querySelector('span').textContent + (sectionId === 'query-section' ? ' with Documents' : ' Documents');
                }
                initQueryPage();
                initDocumentsPage();
            });
        });
        initDocumentsPage();
});

// ==========================================
// DOCUMENTS PAGE FUNCTIONALITY
// ==========================================

function initDocumentsPage() {
    console.log('Initializing Documents Page');
    
    // Set up event listeners
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleDocumentUpload);
    }
    
    // Set up drag and drop functionality
    setupDragAndDrop();
    
    // Set up URL form
    const urlForm = document.getElementById('url-form');
    if (urlForm) {
        urlForm.addEventListener('submit', handleUrlSubmit);
    }
    
    // Load existing documents
    loadDocuments();
}

function setupDragAndDrop() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    
    if (!dropArea || !fileInput) return;
    
    // Prevent default behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop area when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    dropArea.addEventListener('click', () => fileInput.click(), false);
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            uploadFile(files[0]);
        }
    }
    
    // Handle file input change
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            uploadFile(this.files[0]);
        }
    });
}

async function uploadFile(file) {
    if (!file) return;
    
    try {
        // Show loading overlay with specific message
        showLoadingOverlay('Uploading document...');
        
        // Show progress bar
        const progressBar = document.getElementById('upload-progress');
        const progressBarInner = document.getElementById('upload-progress-bar');
        if (progressBar) progressBar.style.display = 'block';
        if (progressBarInner) progressBarInner.style.width = '0%';
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Create XMLHttpRequest to track upload progress
        const xhr = new XMLHttpRequest();
        
        // Setup progress tracking
        xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
                const percentComplete = Math.round((event.loaded / event.total) * 100);
                if (progressBarInner) {
                    progressBarInner.style.width = percentComplete + '%';
                }
            }
        });
        
        // Create a promise to handle the XHR response
        const uploadPromise = new Promise((resolve, reject) => {
            xhr.open('POST', '/api/documents');
            
            xhr.onload = function() {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        reject(new Error('Invalid response format'));
                    }
                } else {
                    reject(new Error(`HTTP error! status: ${xhr.status}`));
                }
            };
            
            xhr.onerror = function() {
                reject(new Error('Network error occurred'));
            };
            
            xhr.send(formData);
        });
        
        const result = await uploadPromise;
        
        // Simulate a slight delay to show the completed progress bar
        await new Promise(resolve => setTimeout(resolve, 500));
        
        showToast('Document uploaded successfully!', 'success');
        
        // Update recent uploads
        updateRecentUploads(result);
        
        // Reload documents list
        loadDocuments();
    } catch (error) {
        console.error('Error uploading document:', error);
        showToast('Error uploading document. Please try again.', 'error');
    } finally {
        // Hide progress bar after a short delay
        setTimeout(() => {
            const progressBar = document.getElementById('upload-progress');
            if (progressBar) progressBar.style.display = 'none';
        }, 1000);
        
        hideLoadingOverlay();
    }
}

async function handleUrlSubmit(event) {
    event.preventDefault();
    
    const urlInput = document.getElementById('url-input');
    if (!urlInput || !urlInput.value.trim()) {
        showToast('Please enter a valid URL.', 'warning');
        return;
    }
    
    const url = urlInput.value.trim();
    
    try {
        // Show loading overlay with specific message
        showLoadingOverlay('Processing URL...');
        
        const response = await fetch('/api/documents/url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        showToast('URL processed successfully!', 'success');
        
        // Clear input
        urlInput.value = '';
        
        // Update recent uploads
        updateRecentUploads(result);
        
        // Reload documents list
        loadDocuments();
    } catch (error) {
        console.error('Error processing URL:', error);
        showToast('Error processing URL. Please try again.', 'error');
    } finally {
        hideLoadingOverlay();
    }
}

function updateRecentUploads(doc) {
    const recentUploads = document.getElementById('recent-uploads');
    if (!recentUploads) return;
    
    // Clear 'no recent uploads' message if present
    if (recentUploads.querySelector('.text-muted')) {
        recentUploads.innerHTML = '';
    }
    
    // Create new upload item
    const uploadItem = document.createElement('div');
    uploadItem.className = 'recent-upload-item';
    uploadItem.innerHTML = `
        <div class="upload-name">${doc.file_name}</div>
        <div class="upload-time">Just now</div>
    `;
    
    // Add to the top of the list
    if (recentUploads.firstChild) {
        recentUploads.insertBefore(uploadItem, recentUploads.firstChild);
    } else {
        recentUploads.appendChild(uploadItem);
    }
    
    // Limit to 5 recent uploads
    const items = recentUploads.querySelectorAll('.recent-upload-item');
    if (items.length > 5) {
        for (let i = 5; i < items.length; i++) {
            recentUploads.removeChild(items[i]);
        }
    }
}

async function loadDocuments() {
    try {
        showLoadingOverlay();
        
        const response = await fetch('/api/documents');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayDocuments(data.documents);
    } catch (error) {
        console.error('Error loading documents:', error);
        showToast('Error loading documents. Please try again.', 'error');
    } finally {
        hideLoadingOverlay();
    }
}

function displayDocuments(documents) {
    const documentsTableBody = document.getElementById('documents-table-body');
    if (!documentsTableBody) return;
    
    documentsTableBody.innerHTML = '';
    
    if (documents.length === 0) {
        documentsTableBody.innerHTML = '<tr><td colspan="5" class="text-center">No documents uploaded yet.</td></tr>';
        return;
    }
    
    documents.forEach(doc => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${doc.file_name}</td>
            <td>${doc.mime_type}</td>
            <td>${formatDate(doc.created_at)}</td>
            <td><span class="status-badge status-${doc.status || 'uploaded'}">${doc.status || 'uploaded'}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-document" data-id="${doc.document_id}">View</button>
                <button class="btn btn-sm btn-outline-danger delete-document" data-id="${doc.document_id}">Delete</button>
            </td>
        `;
        
        documentsTableBody.appendChild(row);
        
        // Add event listeners to buttons
        const viewBtn = row.querySelector('.view-document');
        const deleteBtn = row.querySelector('.delete-document');
        
        viewBtn.addEventListener('click', () => viewDocument(doc.document_id));
        deleteBtn.addEventListener('click', () => deleteDocument(doc.document_id));
    });
}

async function viewDocument(documentId) {
    try {
        showLoadingOverlay();
        
        const response = await fetch(`/api/documents/${documentId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const documentResult = await response.json();
        displayDocumentDetails(documentResult);
    } catch (error) {
        console.error('Error fetching document details:', error);
        showToast('Error loading document details. Please try again.', 'error');
    } finally {
        hideLoadingOverlay();
    }
}

function displayDocumentDetails(doc) {
    const modal = document.getElementById('document-modal');
    const modalTitle = modal.querySelector('.modal-title');
    const modalBody = modal.querySelector('.modal-body');
    
    modalTitle.textContent = doc.file_name;
    
    modalBody.innerHTML = `
        <div class="document-metadata">
            <p><strong>ID:</strong> ${doc.document_id}</p>
            <p><strong>Type:</strong> ${doc.mime_type}</p>
            <p><strong>Uploaded:</strong> ${formatDate(doc.created_at)}</p>
        </div>
        <div class="document-content">
            <h5>Content Analysis:</h5>
            <div class="content-analysis">${doc.analysis || 'No analysis available'}</div>
        </div>
    `;
    
    // Show the modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

async function deleteDocument(documentId) {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoadingOverlay();
        
        const response = await fetch(`/api/documents/${documentId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showToast('Document deleted successfully!', 'success');
        loadDocuments();
    } catch (error) {
        console.error('Error deleting document:', error);
        showToast('Error deleting document. Please try again.', 'error');
    } finally {
        hideLoadingOverlay();
    }
}

// ==========================================
// ANALYSIS PAGE FUNCTIONALITY
// ==========================================

// function initAnalysisPage() {
//     console.log('Initializing Analysis Page');
    
//     // Set up event listeners
//     const analysisForm = document.getElementById('analysis-form');
//     if (analysisForm) {
//         analysisForm.addEventListener('submit', handleAnalysisSubmit);
//     }
    
//     // Load documents for selection
//     loadDocumentsForAnalysis();
    
//     // Load existing analysis sessions
//     loadAnalysisSessions();
// }

async function loadDocumentsForAnalysis() {
    try {
        const response = await fetch('/api/documents');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        populateDocumentSelection(data.documents);
    } catch (error) {
        console.error('Error loading documents for analysis:', error);
        showToast('Error loading documents. Please try again.', 'error');
    }
}

function populateDocumentSelection(documents) {
    const documentSelection = document.getElementById('document-selection');
    if (!documentSelection) return;
    
    documentSelection.innerHTML = '';
    
    if (documents.length === 0) {
        documentSelection.innerHTML = '<div class="no-documents">No documents available for analysis. Please upload documents first.</div>';
        return;
    }
    
    documents.forEach(doc => {
        const docElement = document.createElement('div');
        docElement.className = 'form-check';
        docElement.innerHTML = `
            <input class="form-check-input" type="checkbox" value="${doc.document_id}" id="doc-${doc.document_id}" name="document_ids">
            <label class="form-check-label" for="doc-${doc.document_id}">
                ${doc.file_name}
            </label>
        `;
        
        documentSelection.appendChild(docElement);
    });
}

// async function handleAnalysisSubmit(event) {
//     event.preventDefault();
    
//     const form = event.target;
//     const checkboxes = form.querySelectorAll('input[name="document_ids"]:checked');
//     const contextInput = document.getElementById('analysis-context');
    
//     if (checkboxes.length === 0) {
//         showToast('Please select at least one document for analysis.', 'warning');
//         return;
//     }
    
//     const documentIds = Array.from(checkboxes).map(cb => cb.value);
//     const context = contextInput ? contextInput.value : '';
    
//     try {
//         showLoadingOverlay();
        
//         const response = await fetch('/api/analysis', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({
//                 document_ids: documentIds,
//                 context: context
//             })
//         });
        
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
        
//         const result = await response.json();
//         showToast('Analysis completed successfully!', 'success');
        
//         // Reset form and reload analysis sessions
//         form.reset();
//         loadAnalysisSessions();
        
//         // Show the analysis results
//         displayAnalysisResults(result);
//     } catch (error) {
//         console.error('Error performing analysis:', error);
//         showToast('Error performing analysis. Please try again.', 'error');
//     } finally {
//         hideLoadingOverlay();
//     }
// }

// async function loadAnalysisSessions() {
//     try {
//         showLoadingOverlay();
        
//         const response = await fetch('/api/analysis/sessions');
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
        
//         const data = await response.json();
//         displayAnalysisSessions(data);
//     } catch (error) {
//         console.error('Error loading analysis sessions:', error);
//         showToast('Error loading analysis sessions. Please try again.', 'error');
//     } finally {
//         hideLoadingOverlay();
//     }
// }

// function displayAnalysisSessions(sessions) {
//     const sessionsList = document.getElementById('analysis-sessions');
//     if (!sessionsList) return;
    
//     sessionsList.innerHTML = '';
    
//     if (sessions.length === 0) {
//         sessionsList.innerHTML = '<div class="no-sessions">No analysis sessions yet.</div>';
//         return;
//     }
    
//     sessions.forEach(session => {
//         const sessionElement = document.createElement('div');
//         sessionElement.className = 'analysis-session-item';
//         sessionElement.setAttribute('data-id', session.id);
//         sessionElement.innerHTML = `
//             <div class="session-info">
//                 <div class="session-date">${formatDate(session.created_at)}</div>
//                 <div class="session-summary">${session.summary}</div>
//             </div>
//         `;
        
//         sessionsList.appendChild(sessionElement);
        
//         // Add click event to view session details
//         sessionElement.addEventListener('click', () => selectAnalysisSession(session.id));
//     });
// }

// async function selectAnalysisSession(sessionId) {
//     try {
//         showLoadingOverlay();
        
//         const response = await fetch(`/api/analysis/sessions/${sessionId}`);
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
        
//         const session = await response.json();
//         displayAnalysisResults(session);
        
//         // Highlight the selected session
//         const sessionItems = document.querySelectorAll('.analysis-session-item');
//         sessionItems.forEach(item => {
//             item.classList.remove('selected');
//             if (item.getAttribute('data-id') === sessionId) {
//                 item.classList.add('selected');
//             }
//         });
//     } catch (error) {
//         console.error('Error fetching session details:', error);
//         showToast('Error loading session details. Please try again.', 'error');
//     } finally {
//         hideLoadingOverlay();
//     }
// }

// function displayAnalysisResults(analysis) {
//     const resultsContainer = document.getElementById('analysis-results');
//     if (!resultsContainer) return;
    
//     resultsContainer.innerHTML = '';
    
//     // Create header with summary
//     const header = document.createElement('div');
//     header.className = 'analysis-header';
//     header.innerHTML = `
//         <h3>Analysis Summary</h3>
//         <div class="analysis-summary">${analysis.summary}</div>
//         <div class="analysis-meta">
//             <span class="analysis-id">ID: ${analysis.analysis_id}</span>
//             <span class="analysis-date">Date: ${formatDate(analysis.created_at)}</span>
//         </div>
//     `;
    
//     resultsContainer.appendChild(header);
    
//     // Create insights section
//     const insightsSection = document.createElement('div');
//     insightsSection.className = 'analysis-insights';
//     insightsSection.innerHTML = '<h3>Key Insights</h3>';
    
//     const insightsList = document.createElement('div');
//     insightsList.className = 'insights-list';
    
//     analysis.insights.forEach(insight => {
//         const insightElement = document.createElement('div');
//         insightElement.className = `insight-item insight-${insight.type}`;
//         insightElement.innerHTML = `
//             <div class="insight-type">${insight.type}</div>
//             <div class="insight-content">${insight.content}</div>
//         `;
        
//         insightsList.appendChild(insightElement);
//     });
    
//     insightsSection.appendChild(insightsList);
//     resultsContainer.appendChild(insightsSection);
    
//     // Add a button to query this analysis
//     const queryButton = document.createElement('button');
//     queryButton.className = 'btn btn-primary mt-4';
//     queryButton.textContent = 'Chat with these documents';
//     queryButton.addEventListener('click', () => {
//         window.location.href = `/?session=${analysis.analysis_id}`;
//     });
    
//     resultsContainer.appendChild(queryButton);
    
//     // Show the results container
//     resultsContainer.style.display = 'block';
// }

// ==========================================
// QUERY PAGE FUNCTIONALITY
// ==========================================

function initQueryPage() {
    console.log('Initializing Query Page');
    
    // Set up event listeners
    const sidebarToggle = document.getElementById('toggle-sidebar-btn');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleQuerySidebar);
    }
    
    const clearChatBtn = document.getElementById('clear-chat-btn');
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', confirmClearChat);
    }
    
    // Load documents for selection
    loadDocumentsForChat();
    clearChat();
    // Add initial system message
    addSystemMessage('Select documents from the sidebar to start chatting.');
    
    // Set up query form
    const queryForm = document.getElementById('query-form');
    if (queryForm) {
        queryForm.addEventListener('submit', handleQuerySubmit);
    }
}

async function loadDocumentsForChat() {
    try {
        const response = await fetch('/api/documents');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        populateDocumentSelectionList(data.documents);
    } catch (error) {
        console.error('Error loading documents for chat:', error);
        showToast('Error loading documents. Please try again.', 'error');
    }
}

function populateDocumentSelectionList(documents) {
    const documentList = document.getElementById('document-selection-list');
    if (!documentList) return;
    
    documentList.innerHTML = '';
    
    if (documents.length === 0) {
        documentList.innerHTML = '<div class="no-documents">No documents available. Please upload documents first.</div>';
        return;
    }
    
    documents.forEach(doc => {
        const docElement = document.createElement('div');
        docElement.className = 'document-selection-item';
        docElement.innerHTML = `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" value="${doc.document_id}" id="doc-${doc.document_id}" name="document_ids">
                <label class="form-check-label" for="doc-${doc.document_id}">
                    ${doc.file_name}
                </label>
            </div>
        `;
        
        documentList.appendChild(docElement);
        
        // Add event listener to checkbox
        const checkbox = docElement.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', updateSelectedDocuments);
    });
}

function updateSelectedDocuments() {
    const checkboxes = document.querySelectorAll('#document-selection-list input[type="checkbox"]:checked');
    const selectedDocumentIds = Array.from(checkboxes).map(cb => cb.value);
    
    // Update UI based on selection
    const queryInput = document.getElementById('query-input');
    const querySubmit = document.getElementById('query-submit');
    const selectedDocsInfo = document.getElementById('selected-documents-info');
    
    if (selectedDocumentIds.length > 0) {
        if (queryInput) queryInput.disabled = false;
        if (querySubmit) querySubmit.disabled = false;
        if (selectedDocsInfo) {
            selectedDocsInfo.textContent = `${selectedDocumentIds.length} document(s) selected`;
        }
    } else {
        if (queryInput) queryInput.disabled = true;
        if (querySubmit) querySubmit.disabled = true;
        if (selectedDocsInfo) {
            selectedDocsInfo.textContent = 'No documents selected';
        }
    }
}

async function handleQuerySubmit(event) {
    event.preventDefault();
    
    const queryInput = document.getElementById('query-input');
    if (!queryInput || !queryInput.value.trim()) {
        showToast('Please enter a query.', 'warning');
        return;
    }
    
    const query = queryInput.value.trim();
    
    // Get selected document IDs
    const checkboxes = document.querySelectorAll('#document-selection-list input[type="checkbox"]:checked');
    const documentIds = Array.from(checkboxes).map(cb => cb.value);
    
    if (documentIds.length === 0) {
        showToast('Please select at least one document to query.', 'warning');
        return;
    }
    
    // Add user message to chat
    addUserMessage(query);
    
    // Clear input
    queryInput.value = '';
    
    // Add loading message
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_ids: documentIds,
                query: query
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Remove loading message
        removeLoadingMessage(loadingId);
        
        // Add AI response to chat
        addAIMessage(result.response, result.sources);
    } catch (error) {
        console.error('Error submitting query:', error);
        
        // Remove loading message
        removeLoadingMessage(loadingId);
        
        // Add error message
        addErrorMessage('Error processing your query. Please try again.');
    }
}

function toggleQuerySidebar() {
    const querySidebar = document.querySelector('.query-sidebar');
    const queryMain = document.querySelector('.query-main');
    const toggleBtn = document.getElementById('toggle-sidebar-btn');
    
    if (querySidebar && queryMain) {
        querySidebar.classList.toggle('collapsed');
        queryMain.classList.toggle('expanded');
        
        if (toggleBtn) {
            if (querySidebar.classList.contains('collapsed')) {
                toggleBtn.innerHTML = '<i class="bi bi-chevron-right"></i>';
            } else {
                toggleBtn.innerHTML = '<i class="bi bi-chevron-left"></i>';
            }
        }
    }
}

function confirmClearChat() {
    if (confirm('Are you sure you want to clear the chat? This will remove all messages.')) {
        clearChat();
    }
}

function clearChat() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.innerHTML = '';
        // addSystemMessage('Chat cleared. You can continue asking questions about the selected documents.');
    }
}

// Add a system message to the chat
function addSystemMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message system-message';
    messageElement.innerHTML = `
        <div class="message-content">
            <div class="message-text">${message}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollChatToBottom();
}

// Add a user message to the chat
function addUserMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message user-message';
    messageElement.innerHTML = `
        <div class="message-avatar">
            <i class="fa fa-user"></i>
        </div>
        <div class="message-content">
            <div class="message-sender">You</div>
            <div class="message-text">${message}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollChatToBottom();
}

// Add an AI message to the chat
function addAIMessage(message, sources = []) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    // Convert markdown to HTML using marked instead of showdown
    const htmlMessage = marked.parse(message);
    
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message ai-message';
    
    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="message-sources">
                <div class="sources-header">Sources:</div>
                <ul class="sources-list">
                    ${sources.map(source => `<li>${source.file_name}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    messageElement.innerHTML = `
        <div class="message-avatar">
            <i class="fa fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${htmlMessage}</div>
            ${sourcesHtml}
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollChatToBottom();
}

// Add a loading message to the chat
function addLoadingMessage() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return null;
    
    const id = 'loading-' + Date.now();
    
    const messageElement = document.createElement('div');
    messageElement.id = id;
    messageElement.className = 'chat-message ai-message loading-message';
    messageElement.innerHTML = `
        <div class="message-avatar">
            <i class="fa fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-sender">MCP AI</div>
            <div class="message-text">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollChatToBottom();
    
    return id;
}

// Remove a loading message from the chat
function removeLoadingMessage(id) {
    if (!id) return;
    
    const messageElement = document.getElementById(id);
    if (messageElement) {
        messageElement.parentNode.removeChild(messageElement);
    }
}

// Add an error message to the chat
function addErrorMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = 'chat-message error-message';
    messageElement.innerHTML = `
        <div class="message-content">
            <div class="message-text">${message}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageElement);
    scrollChatToBottom();
}

// Scroll the chat to the bottom
function scrollChatToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Format a date string
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Show a loading overlay
function showLoadingOverlay(message = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    
    if (loadingText) {
        loadingText.textContent = message;
    }
    
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

// Hide the loading overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Show a toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = message;
    
    document.body.appendChild(toast);
    
    // Trigger reflow to enable transition
    toast.offsetHeight;
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}