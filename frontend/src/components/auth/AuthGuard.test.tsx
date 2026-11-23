import { render, screen } from "@testing-library/react";
import type { Session } from "@supabase/supabase-js";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthGuard } from "@/components/auth/AuthGuard";
import { useAuth } from "@/components/auth/AuthProvider";

const replaceMock = vi.fn();

vi.mock("next/navigation", () => ({ useRouter: () => ({ replace: replaceMock }) }));
vi.mock("@/components/auth/AuthProvider", () => ({ useAuth: vi.fn() }));

const useAuthMock = vi.mocked(useAuth);

function mockAuth(session: Session | null, isLoading: boolean): void {
  useAuthMock.mockReturnValue({ session, isLoading, signOut: vi.fn() });
}

describe("AuthGuard", () => {
  beforeEach(() => {
    replaceMock.mockReset();
  });

  it("waits for the session without redirecting or showing the page", () => {
    mockAuth(null, true);

    render(<AuthGuard>secret page</AuthGuard>);

    expect(screen.queryByText("secret page")).toBeNull();
    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("redirects to /login and hides the page when there is no session", () => {
    mockAuth(null, false);

    render(<AuthGuard>secret page</AuthGuard>);

    expect(screen.queryByText("secret page")).toBeNull();
    expect(replaceMock).toHaveBeenCalledWith("/login");
  });

  it("shows the page when signed in", () => {
    mockAuth({ access_token: "token" } as Session, false);

    render(<AuthGuard>secret page</AuthGuard>);

    expect(screen.getByText("secret page")).toBeTruthy();
    expect(replaceMock).not.toHaveBeenCalled();
  });
});
