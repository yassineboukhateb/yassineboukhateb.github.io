// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-teaching",
          title: "teaching",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/teaching/";
          },
        },{id: "news-visited-caidas-university-of-würzburg-germany-for-my-master-s-thesis",
          title: 'Visited CAIDAS, University of Würzburg, Germany, for my master’s thesis.',
          description: "",
          section: "News",},{id: "news-attended-the-geometry-in-data-workshop-at-nantes-université",
          title: 'Attended the Geometry in Data workshop at Nantes Université.',
          description: "",
          section: "News",},{id: "news-attending-the-journées-de-la-statistique-i2e-organized-by-insee-ensae-and-ensai-in-rennes-on-june-9-10-2026",
          title: 'Attending the Journées de la statistique I2E, organized by Insee, ENSAE, and ENSAI...',
          description: "",
          section: "News",},{id: "news-i-will-attend-the-annual-summer-school-on-mathematical-aspects-of-data-science-at-the-institute-for-mathematical-sciences-national-university-of-singapore-from-june-22-to-july-1-2026",
          title: 'I will attend the Annual Summer School on Mathematical Aspects of Data Science...',
          description: "",
          section: "News",},{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
