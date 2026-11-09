import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { SourceProvider } from "./components/sources";
import Library from "./pages/Library";
import { Placeholder } from "./pages/placeholders";

const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: "/", element: <Library /> },
      { path: "/doc/:id/:tab?", element: <Placeholder name="Document" /> },
      { path: "/review", element: <Placeholder name="Review" /> },
      { path: "/progress", element: <Placeholder name="Weak spots" /> },
      { path: "/courses", element: <Placeholder name="Open courses" /> },
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
