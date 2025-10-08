export const dateDiffInDays = (str1, str2) => {
	const date1 = new Date(str1)
	const date2 = new Date(str2)

	const diffMs = date1 - date2;

	const diffDays = diffMs / (1000 * 60 * 60 * 24);

	return diffDays
}

export const toISODate = (dateStr) => {
	try {
		const [day, month, year] = dateStr.split("/");
		const date = new Date(year, month - 1, day);
		
		return date.toISOString().split("T")[0];
	} catch {
		const parsedDate = new Date(dateStr);
		return isNaN(parsedDate.getTime())
			? null
			: parsedDate.toISOString().split("T")[0]
	}
}