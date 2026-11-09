// One function per backend endpoint, grouped by feature.
import { http } from "./client";
import type {
  Answer, Course, DeckStats, Flashcard, Grade, Insights, Knowledge, KukiDocument,
  Question, ReviewButton, SearchHit, Segment, Status, StudyPack,
} from "./types";

export * from "./types";
export { ApiError } from "./client";

const enc = encodeURIComponent;

export const api = {
  status: () => http.get<Status>("/api/status"),

  documents: {
    list: () => http.get<KukiDocument[]>("/api/documents"),
    get: (id: string) => http.get<KukiDocument>(`/api/documents/${enc(id)}`),
    segments: (id: string) => http.get<Segment[]>(`/api/documents/${enc(id)}/segments`),
    upload: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return http.post<KukiDocument>("/api/documents", form);
    },
    remove: (id: string) => http.del(`/api/documents/${enc(id)}`),
    rename: (id: string, title: string) => http.patch<KukiDocument>(`/api/documents/${enc(id)}`, { title }),
    saveAudio: (id: string) => http.post<KukiDocument>(`/api/documents/${enc(id)}/audio`),
    localAudioUrl: (id: string) => `/api/documents/${enc(id)}/audio`,
  },

  pack: {
    get: (docId: string) => http.get<StudyPack>(`/api/documents/${enc(docId)}/pack`),
    generate: (docId: string, knowledge: Knowledge) =>
      http.post<StudyPack>(`/api/documents/${enc(docId)}/pack`, { knowledge }),
    markdownUrl: (docId: string) => `/api/documents/${enc(docId)}/pack/markdown`,
  },

  quiz: {
    list: (docId: string) => http.get<Question[]>(`/api/documents/${enc(docId)}/quiz`),
    generate: (docId: string, count = 5) => http.post<Question[]>(`/api/documents/${enc(docId)}/quiz`, { count }),
    answer: (questionId: number, answer: string) =>
      http.post<Grade>(`/api/questions/${questionId}/answer`, { answer }),
  },

  cards: {
    list: (docId: string) => http.get<Flashcard[]>(`/api/documents/${enc(docId)}/flashcards`),
    generate: (docId: string, count = 12) =>
      http.post<Flashcard[]>(`/api/documents/${enc(docId)}/flashcards`, { count }),
    due: (docId?: string) => http.get<Flashcard[]>(`/api/flashcards/due${docId ? `?document_id=${enc(docId)}` : ""}`),
    stats: (docId?: string) => http.get<DeckStats>(`/api/flashcards/stats${docId ? `?document_id=${enc(docId)}` : ""}`),
    review: (cardId: number, button: ReviewButton) => http.post<Flashcard>(`/api/flashcards/${cardId}/review`, { button }),
    remove: (cardId: number) => http.del(`/api/flashcards/${cardId}`),
    ankiUrl: (docId: string) => `/api/documents/${enc(docId)}/flashcards/anki.txt`,
  },

  insights: (docId?: string) => http.get<Insights>(`/api/insights${docId ? `?document_id=${enc(docId)}` : ""}`),

  ask: (question: string, documentIds?: string[]) =>
    http.post<Answer>("/api/ask", { question, document_ids: documentIds }),

  search: (q: string) => http.get<SearchHit[]>(`/api/search?q=${enc(q)}`),

  courses: {
    list: () => http.get<Course[]>("/api/courses"),
    importLecture: (courseId: string, n: number) =>
      http.post<KukiDocument>(`/api/courses/${enc(courseId)}/lectures/${n}/import`),
  },
};
