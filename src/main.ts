import "./styles.css";

type Role = "user" | "assistant";

type Message = {
  id: string;
  role: Role;
  content: string;
  pending?: boolean;
  attachments?: Attachment[];
};

type Chat = {
  id: string;
  title: string;
  messages: Message[];
};

type Attachment = {
  id: string;
  name: string;
  type: string;
  size: number;
  content: string;
};

const MODEL = "llama3.2:3b";

const logoSvg = `
<svg viewBox="0 0 40 40" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="kuki-dot-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="1.1" flood-color="#0F172A" flood-opacity=".13"/>
    </filter>
  </defs>
  <g filter="url(#kuki-dot-shadow)">
    <circle cx="20" cy="21" r="6.1" fill="#111111"/>
    <circle cx="20" cy="8.6" r="4.3" fill="#111111"/>
    <circle cx="30.7" cy="26.8" r="4.3" fill="#2563EB"/>
    <circle cx="9.3" cy="26.8" r="4.3" fill="#14B8A6"/>
  </g>
  <path d="M20 14.2v-2.1M25.2 24.2l2 1.1M14.8 24.2l-2 1.1" fill="none" stroke="#111111" stroke-width="1.8" stroke-linecap="round" opacity=".26"/>
</svg>
`;

const editIcon = `
<svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M18.4 2.6a2.1 2.1 0 0 1 3 3L12 15l-4 1 1-4 9.4-9.4Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
`;

const sendIcon = `
<svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <path d="M12 19V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <path d="m5 12 7-7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
`;

const plusIcon = `
<svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
`;

const sidebarIcon = `
<svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <rect x="3.5" y="4" width="17" height="16" rx="3" stroke="currentColor" stroke-width="1.8"/>
  <path d="M9 4v16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>
`;

let chats: Chat[] = [newChat()];
let activeChatId = chats[0].id;
let aiReady = false;
let aiMessage = "Checking AI...";
let sidebarCollapsed = false;
let selectedAttachments: Attachment[] = [];

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) {
  throw new Error("App root not found");
}
const root = app;

function newId(prefix: string): string {
  return `${prefix}-${crypto.randomUUID()}`;
}

function newChat(): Chat {
  return {
    id: newId("chat"),
    title: "New chat",
    messages: [],
  };
}

function activeChat(): Chat {
  const found = chats.find((chat) => chat.id === activeChatId);
  if (!found) {
    const chat = newChat();
    chats.unshift(chat);
    activeChatId = chat.id;
    return chat;
  }
  return found;
}

function shortTitle(text: string): string {
  const cleaned = text.replace(/\s+/g, " ").trim();
  return cleaned.length > 36 ? `${cleaned.slice(0, 36).trim()}...` : cleaned || "New chat";
}

function isEmptyChat(chat: Chat): boolean {
  return chat.messages.length === 0;
}

function startNewChat(): void {
  const current = activeChat();
  if (isEmptyChat(current)) {
    render();
    return;
  }

  const existingDraft = chats.find(isEmptyChat);
  if (existingDraft) {
    activeChatId = existingDraft.id;
    render();
    return;
  }

  const chat = newChat();
  chats.unshift(chat);
  activeChatId = chat.id;
  render();
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function stripDecorativeMarkdown(value: string): string {
  return value
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .trim();
}

function renderInlineText(value: string): string {
  return escapeHtml(stripDecorativeMarkdown(value)).replace(/`([^`]+)`/g, "<code>$1</code>");
}

function renderMessageText(value: string): string {
  const normalized = value
    .trim();
  const parts = normalized.split(/```([\s\S]*?)```/g);
  return parts
    .map((part, index) => {
      if (index % 2 === 1) {
        return `<pre><code>${escapeHtml(part.trim())}</code></pre>`;
      }
      return renderInlineText(part);
    })
    .join("");
}

function formatFileSize(size: number): string {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function renderAttachments(attachments: Attachment[] = []): string {
  if (!attachments.length) return "";
  return `
    <div class="message-files" aria-label="Attached files">
      ${attachments
        .map(
          (file) => `
            <span class="message-file">
              <span class="file-name">${escapeHtml(file.name)}</span>
              <span class="file-size">${formatFileSize(file.size)}</span>
            </span>
          `,
        )
        .join("")}
    </div>
  `;
}

function selectedAttachmentContext(): string {
  if (!selectedAttachments.length) return "";
  return selectedAttachments
    .map((file) => {
      const text = file.content.trim() || "No readable text was extracted in the browser.";
      return `File: ${file.name}\nType: ${file.type || "unknown"}\nContent:\n${text.slice(0, 12000)}`;
    })
    .join("\n\n");
}

function render(): void {
  const chat = activeChat();
  const messages = chat.messages
    .map((message) => {
      const content = message.pending
        ? `<div class="thinking" aria-label="Kuki is thinking"><span class="thinking-mark">${logoSvg}</span></div>`
        : renderMessageText(message.content);

      return `
        <div class="message-row ${message.role}">
          <div class="bubble">${renderAttachments(message.attachments)}${content}</div>
        </div>
      `;
    })
    .join("");

  const history = chats
    .filter((item) => !isEmptyChat(item))
    .map(
      (item) => `
        <button class="history-button" data-chat-id="${item.id}" type="button">
          <span>${escapeHtml(item.title)}</span>
        </button>
      `,
    )
    .join("");

  root.innerHTML = `
    <div class="app ${sidebarCollapsed ? "sidebar-collapsed" : ""}">
      <aside class="sidebar">
        <section class="sidebar-top">
          <div class="sidebar-head">
            <h1 class="sidebar-title">Kuki</h1>
            <button class="sidebar-toggle" data-toggle-sidebar type="button" aria-label="${sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}">${sidebarIcon}</button>
          </div>
          <button class="new-chat-button" data-new-chat type="button" aria-label="New chat">${editIcon}<span>New chat</span></button>
        </section>
        <section class="sidebar-section">
          <h2 class="sidebar-heading">History</h2>
          ${history}
        </section>
      </aside>
      <main class="main">
        <header class="topbar">
          <div class="brand">
            <div class="logo">${logoSvg}</div>
            <div class="brand-name">Kuki</div>
          </div>
          <button class="top-new-chat" data-new-chat type="button">${editIcon}<span>New chat</span></button>
        </header>
        <section class="messages" data-messages>
          <div class="messages-inner">
            ${messages || '<div class="empty-space" aria-hidden="true"></div>'}
          </div>
        </section>
        <footer class="composer-wrap">
          <form class="composer" data-composer>
            <div class="attachment-tray" data-attachment-tray ${selectedAttachments.length ? "" : "hidden"}>
              ${selectedAttachments
                .map(
                  (file) => `
                    <span class="attachment-chip">
                      <span class="file-name">${escapeHtml(file.name)}</span>
                      <span class="file-size">${formatFileSize(file.size)}</span>
                      <button class="remove-attachment" type="button" data-remove-attachment="${file.id}" aria-label="Remove ${escapeHtml(file.name)}">&times;</button>
                    </span>
                  `,
                )
                .join("")}
            </div>
            <input class="file-input" type="file" data-file-input multiple hidden />
            <button class="attach-button" type="button" data-attach aria-label="Upload files" title="Upload files">${plusIcon}</button>
            <textarea aria-label="Message Kuki" placeholder="Message Kuki" rows="1" data-input></textarea>
            <button class="send-button" type="submit" data-send disabled>${sendIcon}</button>
          </form>
        </footer>
      </main>
    </div>
  `;

  bindEvents();
  scrollToBottom();
}

function applySidebarState(): void {
  const appShell = document.querySelector<HTMLElement>(".app");
  const toggle = document.querySelector<HTMLButtonElement>("[data-toggle-sidebar]");

  appShell?.classList.toggle("sidebar-collapsed", sidebarCollapsed);
  toggle?.setAttribute("aria-label", sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar");
}

function bindEvents(): void {
  document.querySelectorAll<HTMLButtonElement>("[data-new-chat]").forEach((button) => {
    button.addEventListener("click", startNewChat);
  });

  document.querySelectorAll<HTMLButtonElement>("[data-toggle-sidebar]").forEach((button) => {
    button.addEventListener("click", () => {
      sidebarCollapsed = !sidebarCollapsed;
      applySidebarState();
    });
  });

  document.querySelectorAll<HTMLButtonElement>("[data-chat-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.chatId;
      if (!id) return;
      activeChatId = id;
      render();
    });
  });

  const form = document.querySelector<HTMLFormElement>("[data-composer]");
  const input = document.querySelector<HTMLTextAreaElement>("[data-input]");
  const send = document.querySelector<HTMLButtonElement>("[data-send]");
  const attach = document.querySelector<HTMLButtonElement>("[data-attach]");
  const fileInput = document.querySelector<HTMLInputElement>("[data-file-input]");

  if (!form || !input || !send) return;

  const updateSend = () => {
    send.disabled =
      (input.value.trim().length === 0 && selectedAttachments.length === 0) ||
      activeChat().messages.some((message) => message.pending);
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
  };

  input.addEventListener("input", updateSend);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  attach?.addEventListener("click", () => {
    fileInput?.click();
  });

  fileInput?.addEventListener("change", async () => {
    const files = Array.from(fileInput.files ?? []);
    const attachments = await Promise.all(files.map(readAttachment));
    selectedAttachments = [...selectedAttachments, ...attachments];
    fileInput.value = "";
    render();
  });

  document.querySelectorAll<HTMLButtonElement>("[data-remove-attachment]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.removeAttachment;
      selectedAttachments = selectedAttachments.filter((file) => file.id !== id);
      render();
    });
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const prompt = input.value.trim();
    if (!prompt && selectedAttachments.length === 0) return;
    const attachments = selectedAttachments;
    const context = selectedAttachmentContext();
    const message = prompt || "Uploaded file(s).";
    input.value = "";
    selectedAttachments = [];
    void sendMessage(message, attachments, context);
  });

  updateSend();
  input.focus();
}

function readAttachment(file: File): Promise<Attachment> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    const fallback = {
      id: newId("file"),
      name: file.name,
      type: file.type,
      size: file.size,
      content: "",
    };

    reader.addEventListener("load", () => {
      resolve({ ...fallback, content: String(reader.result ?? "") });
    });
    reader.addEventListener("error", () => {
      resolve(fallback);
    });
    reader.readAsText(file);
  });
}

function scrollToBottom(): void {
  const container = document.querySelector<HTMLElement>("[data-messages]");
  if (!container) return;
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;
  });
}

async function checkAi(): Promise<void> {
  try {
    const response = await fetch("/api/tags");
    if (!response.ok) throw new Error("Ollama is not responding.");
    const payload = (await response.json()) as { models?: Array<{ name?: string }> };
    const models = payload.models?.map((model) => model.name).filter(Boolean) ?? [];
    aiReady = models.includes(MODEL);
    aiMessage = aiReady ? `Ready with ${MODEL}.` : `${MODEL} is not installed in Ollama.`;
  } catch {
    aiReady = false;
    aiMessage = "Start Ollama, then refresh Kuki.";
  }
  render();
}

async function sendMessage(prompt: string, attachments: Attachment[] = [], attachmentContext = ""): Promise<void> {
  const chat = activeChat();
  if (chat.messages.length === 0) {
    chat.title = shortTitle(prompt);
  }

  const userMessageId = newId("msg");
  chat.messages.push({ id: userMessageId, role: "user", content: prompt, attachments });
  const pendingId = newId("msg");
  chat.messages.push({ id: pendingId, role: "assistant", content: "", pending: true });
  render();

  const userContent = attachmentContext
    ? `Uploaded files:\n${attachmentContext}\n\nUser message:\n${prompt}`
    : prompt;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: MODEL,
        stream: false,
        messages: [
          {
            role: "system",
            content:
              "You are Kuki, the user's study pal. Sound warm, clear, and natural, like a helpful friend who is good at studying, research, and everyday tasks. Do not introduce yourself unless asked. Do not start replies with titles, greetings, or headings. Avoid Markdown headings and bold opening lines. Keep answers direct and easy to read.",
          },
          ...chat.messages
            .filter((message) => !message.pending)
            .slice(-10)
            .map((message) => ({
              role: message.role,
              content: message.id === userMessageId ? userContent : message.content,
            })),
        ],
        options: { temperature: 0.35, num_ctx: 4096 },
      }),
    });

    if (!response.ok) throw new Error("The AI runtime returned an error.");
    const payload = (await response.json()) as { message?: { content?: string } };
    updateMessage(pendingId, payload.message?.content?.trim() || "I could not produce a response. Please try again.");
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Something went wrong.";
    updateMessage(pendingId, `I could not reach the AI runtime just now.\n\n${detail}`);
  }
}

function updateMessage(id: string, content: string): void {
  const chat = activeChat();
  const message = chat.messages.find((item) => item.id === id);
  if (!message) return;
  message.pending = false;
  message.content = content;
  render();
}

function installFavicon(): void {
  const svg = encodeURIComponent(logoSvg);
  const link = document.createElement("link");
  link.rel = "icon";
  link.type = "image/svg+xml";
  link.href = `data:image/svg+xml,${svg}`;
  document.head.append(link);
}

installFavicon();
render();
void checkAi();
