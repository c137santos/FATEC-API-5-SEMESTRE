export const dateDiffInDays = (str1, str2) => {
	const date1 = new Date(str1)
	const date2 = new Date(str2)

	const diffMs = date1 - date2;

	const diffDays = diffMs / (1000 * 60 * 60 * 24);

	return diffDays
}

export const toISODate = (dateStr) => {
  const [day, month, year] = dateStr.split("/");
  return new Date(year, month - 1, day).toISOString().split("T")[0];
}