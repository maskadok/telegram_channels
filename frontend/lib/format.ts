const numberFormatter = new Intl.NumberFormat("en-US");
const dateFormatter = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});


export function formatNumber(value: number): string {
  return numberFormatter.format(value || 0);
}


export function formatDate(value: string | null): string {
  if (!value) {
    return "No date";
  }

  return dateFormatter.format(new Date(value));
}


export function truncateText(value: string | null, maxLength = 180): string {
  if (!value) {
    return "Post without text";
  }

  if (value.length <= maxLength) {
    return value;
  }

  return `${value.slice(0, maxLength).trim()}...`;
}
