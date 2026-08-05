"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Stats from "@/components/Stats";
import AboutPreview from "@/components/AboutPreview";
import WhoCanJoin from "@/components/WhoCanJoin";
import WhyChooseUs from "@/components/WhyChooseUs";
import FeaturedCourses from "@/components/FeaturedCourses";
import LearningJourney from "@/components/LearningJourney";
import Placements from "@/components/Placements";
import ReviewSection from "@/components/ReviewSection";
import FAQ from "@/components/FAQ";
import FinalCTA from "@/components/FinalCTA";
import Footer from "@/components/Footer";
import EnrollModal from "@/components/EnrollModal";

export default function Home() {
  const [isEnrollModalOpen, setIsEnrollModalOpen] = useState(false);
  const [defaultCourse, setDefaultCourse] = useState("");

  const openEnrollModal = (courseName?: string) => {
    setDefaultCourse(courseName ?? "");
    toast.success("Enrollment is coming soon. Please check back later.");
    setIsEnrollModalOpen(false);
  };

  const closeEnrollModal = () => {
    setIsEnrollModalOpen(false);
    setDefaultCourse("");
  };

  return (
    <main>
      <Navbar enrollAction={openEnrollModal} />
      <Hero enrollAction={openEnrollModal} />
      <Stats />
      <AboutPreview />
      <WhoCanJoin />
      <WhyChooseUs />
      <FeaturedCourses enrollAction={openEnrollModal} />
      <LearningJourney />
      <Placements />
      <ReviewSection />
      <FAQ />
      <FinalCTA enrollAction={openEnrollModal} />
      <Footer />
      <EnrollModal
        isOpen={isEnrollModalOpen}
        onCloseAction={closeEnrollModal}
        defaultCourse={defaultCourse}
      />
    </main>
  );
}
