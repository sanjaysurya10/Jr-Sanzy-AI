const DUE_FORMAT = new Intl.DateTimeFormat("en-IE", {
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

const TIME_FORMAT = new Intl.DateTimeFormat("en-IE", {
  hour: "2-digit",
  minute: "2-digit",
});

export function formatDue(isoTimestamp: string): string {
  return DUE_FORMAT.format(new Date(isoTimestamp));
}

export function formatTime(isoTimestamp: string): string {
  return TIME_FORMAT.format(new Date(isoTimestamp));
}

function pad(value: number): string {
  return String(value).padStart(2, "0");
}

// <input type="datetime-local"> works in the browser's local time without a zone.
export function toDateTimeLocalValue(isoTimestamp: string | null): string {
  if (isoTimestamp === null) {
    return "";
  }
  const date = new Date(isoTimestamp);
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
    `T${pad(date.getHours())}:${pad(date.getMinutes())}`
  );
}

export function fromDateTimeLocalValue(value: string): string | null {
  return value === "" ? null : new Date(value).toISOString();
}
