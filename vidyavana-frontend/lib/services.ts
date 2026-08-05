import { api, buildMediaUrl, unwrapApiData, unwrapListData } from "@/lib/api";

export type Course = {
  id: number;
  uuid: string;
  name: string;
  slug: string;
  short_description: string;
  duration: string;
  level: string;
  fee: number | string | null;
  image: string | null;
  category: string;
  category_slug: string;
  certificate_included: boolean;
  is_featured: boolean;
  is_active: boolean;
};

export type CourseCategory = {
  id: number;
  name: string;
  slug: string;
  tagline: string;
  icon: string;
  is_active: boolean;
  order: number;
  course_count: number;
};

export type FAQItem = {
  id: number;
  category: number | null;
  category_name: string | null;
  question: string;
  answer: string;
  is_active: boolean;
  order: number;
};

export type Testimonial = {
  id: number;
  uuid: string;
  name: string;
  role_or_course: string;
  course: number | null;
  course_name: string | null;
  photo: string | null;
  quote: string;
  rating: number;
  is_featured: boolean;
  is_active: boolean;
};

export type Review = {
  id: number;
  uuid: string;
  name: string;
  course: number | null;
  course_name: string | null;
  rating: number;
  title: string;
  message: string;
  is_approved: boolean;
};

export type DashboardStats = {
  manual_statistics: Array<{ id: number; key: string; label: string; value: number | string; icon: string; is_active: boolean; order: number }>;
  courses_offered: number;
  course_categories: number;
  total_reviews: number;
  average_rating: number;
  total_testimonials: number;
  languages_supported: number;
};

export type LanguageOption = {
  id: number;
  code: string;
  name: string;
  native_name: string;
  is_default: boolean;
  is_active: boolean;
  order: number;
};

export type ContactPayload = {
  name: string;
  email: string;
  phone: string;
  subject: string;
  message: string;
};

export type EnquiryPayload = {
  name: string;
  email?: string;
  phone: string;
  course: number | null;
  preferred_batch_time?: string;
  message?: string;
  source?: "website";
};

export type ChatMessagePayload = {
  session_uuid?: string | null;
  message: string;
  language_code?: string;
  visitor_name?: string;
  visitor_email?: string;
};

export async function getCourses(): Promise<Course[]> {
  const response = await api.get("/courses/");
  return unwrapListData<Course>(response.data);
}

export async function getCourseCategories(): Promise<CourseCategory[]> {
  const response = await api.get("/courses/categories/");
  return unwrapListData<CourseCategory>(response.data);
}

export async function getFAQs(): Promise<FAQItem[]> {
  const response = await api.get("/faq/");
  return unwrapListData<FAQItem>(response.data);
}

export async function getTestimonials(): Promise<Testimonial[]> {
  const response = await api.get("/testimonials/");
  return unwrapListData<Testimonial>(response.data);
}

export async function getReviews(): Promise<Review[]> {
  const response = await api.get("/reviews/");
  return unwrapListData<Review>(response.data);
}

export async function submitReview(payload: {
  name: string;
  email?: string;
  rating: number;
  title?: string;
  message: string;
}) {
  const response = await api.post("/reviews/", payload);
  return unwrapApiData(response.data);
}

export async function submitFAQQuestion(payload: {
  name?: string;
  email?: string;
  question: string;
}) {
  const response = await api.post("/faq/questions/", payload);
  return unwrapApiData(response.data);
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await api.get("/dashboard/stats/");
  return unwrapApiData<DashboardStats>(response.data);
}

export async function getLanguages(): Promise<LanguageOption[]> {
  const response = await api.get("/languages/");
  return unwrapListData<LanguageOption>(response.data);
}

export async function submitContactMessage(payload: ContactPayload) {
  const response = await api.post("/contact/", payload);
  return unwrapApiData(response.data);
}

export async function submitEnquiry(payload: EnquiryPayload) {
  const response = await api.post("/enquiry/", payload);
  return unwrapApiData(response.data);
}

export async function sendChatbotMessage(payload: ChatMessagePayload) {
  const response = await api.post("/chatbot/message/", payload);
  return unwrapApiData<{ success?: boolean; data?: unknown }>(response.data);
}

export function getCourseImage(course: Course): string | null {
  return buildMediaUrl(course.image);
}
