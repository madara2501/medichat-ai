let currentTab = 0;

const messagesDiv = document.getElementById('messages');
const historyMessages = document.getElementById('history-messages');
const input = document.getElementById('user-input');


function loadWelcome() {

    // GET USER-SPECIFIC SAVED NAME
    let savedName =
        localStorage.getItem(
            "medichat_username_" + userEmail
        );

    // DEFAULT NAME
    if (!savedName) {

        savedName =
            userEmail
            ? userEmail.split("@")[0]
            : "User";
    }

    messagesDiv.innerHTML = `
        <div class="welcome">
            <i class="fa-solid fa-heart-pulse welcome-icon"></i>

            <h2>Hello ${savedName} 👋</h2>

            <p>
                How are you feeling today?
                Tell me about any symptoms.
            </p>
        </div>

        <!-- Typing Indicator -->
        <div class="typing-indicator"
             id="typingIndicator"
             style="display:none;">

            <div class="typing-bubble">
                <span></span>
                <span></span>
                <span></span>
            </div>

        </div>
    `;

    // RECONNECT TYPING INDICATOR
    window.typingIndicator =
        document.getElementById(
            'typingIndicator'
        );
}


// SWITCH TAB
function switchTab(tab) {

    currentTab = tab;

    document.getElementById('chat-tab').style.display =
        tab === 0 ? 'flex' : 'none';

    document.getElementById('history-tab').style.display =
        tab === 1 ? 'flex' : 'none';

    document.getElementById('tab-new')
        .classList.toggle('active', tab === 0);

    document.getElementById('tab-history')
        .classList.toggle('active', tab === 1);

    if (tab === 1) loadHistory();
}


// SEND MESSAGE
async function sendMessage() {

    const text = input.value.trim();

    if (!text) return;

    addMessage(text, true);

    input.value = '';
    // SHOW TYPING
    const typingIndicator =
        document.getElementById('typingIndicator');

    typingIndicator.style.display = 'flex';
    // MOVE TYPING TO BOTTOM
    messagesDiv.appendChild(typingIndicator);

    messagesDiv.scrollTop =
        messagesDiv.scrollHeight;
    messagesDiv.scrollTop =
    messagesDiv.scrollHeight;

    try {

        const res = await fetch('/chat', {
            method: 'POST',

            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({
                message: text
            })
        });

        const data = await res.json();
       document.getElementById(
             'typingIndicator'
       ).style.display = 'none';
        addMessage(data.reply, false);

        // AUTO REFRESH HISTORY
        if (currentTab === 1) {
            loadHistory();
        }

    } catch (e) {

        document.getElementById(
        'typingIndicator'
        ).style.display = 'none';

        addMessage(
            "Sorry, connection error.",
            false
        );
    }
}


// ADD MESSAGE
function addMessage(text, isUser) {

    const div = document.createElement('div');

    div.className =
        `message ${isUser ? 'user' : 'bot'}`;

    if (!isUser) {

        text = text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>")
            .replace(/\* /g, "• ");
    }

    div.innerHTML =
        text.replace(/\n/g, '<br>');

    messagesDiv.appendChild(div);

    messagesDiv.scrollTop =
        messagesDiv.scrollHeight;
}


// LOAD HISTORY
async function loadHistory() {

    try {

        const res = await fetch('/history');

        if (!res.ok) {

            historyMessages.innerHTML =
                "<p>Error loading history</p>";

            return;
        }

        const data = await res.json();

        historyMessages.innerHTML =
            '<h3 style="padding:10px;">Your Chat History</h3>';

        if (data.history && data.history.length > 0) {

            data.history.forEach(item => {

                const div =
                    document.createElement('div');

                div.className = 'history-item';

                div.innerHTML = `
                   <small>${item.time}</small><br>
                   <b>You:</b> ${item.user.replace(/\n/g, '<br>')}<br><br>
                   <b>AI:</b> ${item.bot.replace(/\n/g, '<br>')}
               `;

                historyMessages.appendChild(div);
            });

        } else {

            historyMessages.innerHTML +=
                '<p style="text-align:center;">No history found</p>';
        }

    } catch (err) {

        console.error(err);

        historyMessages.innerHTML =
            "<p>Failed to load history</p>";
    }
}


// CLEAR CHAT
function clearCurrentChat() {

    messagesDiv.innerHTML = '';

    loadWelcome();
}


// CLEAR HISTORY
async function clearAllHistory() {

    if (confirm("Delete ALL history?")) {

        await fetch('/clear_history', {
            method: 'POST'
        });

        loadHistory();

        alert("History cleared!");
    }
}


// LOGOUT
function logout() {

    if (confirm("Logout?")) {

        window.location.href = '/logout';
    }
}


// ENTER KEY SEND
input.addEventListener('keypress', (e) => {

    if (e.key === 'Enter') {

        sendMessage();
    }
});


// PAGE LOAD
document.addEventListener("DOMContentLoaded", () => {

    loadWelcome();

    setAvatarInitials();

    updateBigAvatar();

    // LOAD USER-SPECIFIC SAVED NAME
    const savedName =
        localStorage.getItem(
            "medichat_username_" + userEmail
        );

    if(savedName){

        // UPDATE SIDEBAR
        document.getElementById("username")
            .innerText = savedName;

        // UPDATE DROPDOWN
        const dropdown =
            document.getElementById("dropdownUsername");

        if(dropdown){

            dropdown.innerText = savedName;
        }

        // UPDATE PROFILE INPUT
        document.getElementById("displayName")
            .value = savedName;

        // CREATE INITIALS
        let initials = "";

        const parts = savedName.split(" ");

        if(parts.length === 1){

            initials = parts[0][0];

        } else {

            initials =
                parts[0][0] +
                parts[1][0];
        }

        initials = initials.toUpperCase();

        // UPDATE AVATARS
        document.getElementById("avatar")
            .innerText = initials;

        document.getElementById("avatarBig")
            .innerText = initials;

        document.getElementById("bigProfileAvatar")
            .innerText = initials;

        loadWelcome();
    }
});


// AVATAR INITIALS
function setAvatarInitials() {

    const name =
        document.getElementById("username")
        .innerText
        .trim();

    if (!name) return;

    const parts = name.split(" ");

    let initials = "";

    if (parts.length === 1) {

        initials = parts[0][0];

    } else {

        initials =
            parts[0][0] +
            parts[1][0];
    }

    document.getElementById("avatar")
        .innerText =
        initials.toUpperCase();
}


// TOGGLE PROFILE MENU
function toggleProfileMenu() {

    const menu =
        document.getElementById("profileMenu");

    menu.classList.toggle("show");
}


// CLOSE PROFILE MENU OUTSIDE CLICK
document.addEventListener("click", function(e) {

    const menu =
        document.getElementById("profileMenu");

    const profile =
        document.querySelector(".user-profile");

    if (
        !profile.contains(e.target) &&
        !menu.contains(e.target)
    ) {
        menu.classList.remove("show");
    }
});


// UPDATE BIG AVATAR
function updateBigAvatar() {

    const smallAvatar =
        document.getElementById("avatar")
        .innerText;

    document.getElementById("avatarBig")
        .innerText =
        smallAvatar;
}


// OPEN PROFILE
function showProfile() {

    document.getElementById("profile-page")
        .style.display = "flex";

    document.getElementById("profileMenu")
        .classList.remove("show");
}


// CLOSE PROFILE
function closeProfile() {

    document.getElementById("profile-page")
        .style.display = "none";
}


// SAVE PROFILE
document.getElementById("profileForm")
.addEventListener("submit", function(e){

    e.preventDefault();

    const newName =
        document.getElementById("displayName")
        .value
        .trim();

    if(!newName) return;

    // SAVE USER-SPECIFIC NAME
    localStorage.setItem(
        "medichat_username_" + userEmail,
        newName
    );

    // UPDATE SIDEBAR
    document.getElementById("username")
        .innerText = newName;

    // UPDATE DROPDOWN
    const dropdown =
        document.getElementById("dropdownUsername");

    if(dropdown){

        dropdown.innerText = newName;
    }

    // UPDATE WELCOME
    loadWelcome();

    // CREATE INITIALS
    let initials = "";

    const parts = newName.split(" ");

    if(parts.length === 1){

        initials = parts[0][0];

    } else {

        initials =
            parts[0][0] +
            parts[1][0];
    }

    initials = initials.toUpperCase();

    // UPDATE AVATARS
    document.getElementById("avatar")
        .innerText = initials;

    document.getElementById("avatarBig")
        .innerText = initials;

    document.getElementById("bigProfileAvatar")
        .innerText = initials;

    alert("Profile Updated!");

    closeProfile();

});