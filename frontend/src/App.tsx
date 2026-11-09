import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { SourceProvider } from "./components/sources";
import DocumentPage from "./pages/Document";
import Courses from "./pages/Courses";
import Library from "./pages/Library";
import Progress from "./pages/Progress";
import Review from "./pages/Review";
import { AskPanel } from "./pages/doc/AskPanel";
import { CardsPanel } from "./pages/doc/CardsPanel";
import { PackPanel } from "./pages/doc/PackPanel";
import { QuizPanel } from "./pages/doc/QuizPanel";
import { SourcePanel } from "./pages/doc/SourcePanel";

const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: "/", element: <Library /> },
      {
        path: "/doc/:id/:tab?",
        element: (
          <DocumentPage
            panels={{
              pack: (d) => <PackPanel doc={d} />,
              quiz: (d) => <QuizPanel doc={d} />,
              cards: (d) => <CardsPanel doc={d} />,
              ask: (d) => <AskPanel doc={d} />,
              source: (d) => <SourcePanel doc={d} />,
            }}
          />
        ),
      },
      { path: "/review", element: <Review /> },
      { path: "/progress", element: <Progress /> },
      { path: "/courses", element: <Courses /> },
    ],
  },
]);

export default function App() {
  return (
    <SourceProvider>
      <RouterProvider router={router} />
    </SourceProvider>
  );
}
