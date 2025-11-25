import React from "react";
import Hero from "../components/Hero";
import OCRForm from "../components/OCRForm";
import InfoCards from "../components/InfoCards";
import Guide from "../components/Guide";
import FAQ from "../components/FAQ";
import Comparison from "../components/Comparison";
import Stats from "../components/Stats";
import AdvancedFeatures from "../components/AdvancedFeatures";
import VideoTutorial from "../components/VideoTutorial";

export default function Home() {
    return (
        <>
            <Hero />
            <OCRForm />
            <InfoCards />
            <Guide />
            <FAQ />
            <Comparison />
            <Stats />
            <AdvancedFeatures />
            <VideoTutorial />
        </>
    );
}
