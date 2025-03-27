/**
 * Fetches and displays PageSpeed Insights data.
 * Enable PageSpeed Insights API - https://developers.google.com/speed/docs/insights/v5/get-started
 */
async function run() {
    const apiEndpoint =
        'https://www.googleapis.com/pagespeedonline/v5/runPagespeed';
    const targetUrl = 'https://www.misterrubato.com/test/testfilbert.html';
  
    const url = new URL(apiEndpoint);
    url.searchParams.set('url', targetUrl);
  
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const json = await response.json();
  
      // See
      // https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed#response
      // to learn more about each of the properties in the response object.
  
      showInitialContent(json.id);
  
      const cruxMetrics = {
        'First Contentful Paint':
            json.loadingExperience.metrics.FIRST_CONTENTFUL_PAINT_MS?.category,
        'Interaction to Next Paint':
            json.loadingExperience.metrics.INTERACTION_TO_NEXT_PAINT?.category,
      };
      showCruxContent(cruxMetrics);
  
      const lighthouse = json.lighthouseResult;
      const lighthouseMetrics = {
        'First Contentful Paint':
            lighthouse.audits['first-contentful-paint']?.displayValue,
        'Speed Index': lighthouse.audits['speed-index']?.displayValue,
        'Largest Contentful Paint':
            lighthouse.audits['largest-contentful-paint']?.displayValue,
        'Total Blocking Time':
            lighthouse.audits['total-blocking-time']?.displayValue,
        'Time To Interactive': lighthouse.audits['interactive']?.displayValue,
      };
      showLighthouseContent(lighthouseMetrics);
    } catch (error) {
      console.error('Fetching PageSpeed Insights failed:', error);
      document.body.textContent =
          `Failed to fetch PageSpeed data. Check the console for errors.`;
    }
  }
  
  /**
   * Displays initial content, including the page ID.
   * @param {string} id The ID of the page being tested.
   */
  function showInitialContent(id) {
    document.body.innerHTML = '';  // Clear previous content
    const title = document.createElement('h1');
    title.textContent = 'PageSpeed Insights API Demo';
    document.body.appendChild(title);
  
    const page = document.createElement('p');
    page.textContent = `Page tested: ${id}`;
    document.body.appendChild(page);
  }
  
  /**
   * Displays CrUX metrics.
   * @param {!Object} cruxMetrics The CrUX metrics to display.
   */
  function showCruxContent(cruxMetrics) {
    const cruxHeader = document.createElement('h2');
    cruxHeader.textContent = 'Chrome User Experience Report Results';
    document.body.appendChild(cruxHeader);
  
    for (const key in cruxMetrics) {
      const p = document.createElement('p');
      p.textContent = `${key}: ${cruxMetrics[key]}`;
      document.body.appendChild(p);
    }
  }
  
  /**
   * Displays Lighthouse metrics.
   * @param {!Object} lighthouseMetrics The Lighthouse metrics to display.
   */
  function showLighthouseContent(lighthouseMetrics) {
    const lighthouseHeader = document.createElement('h2');
    lighthouseHeader.textContent = 'Lighthouse Results';
    document.body.appendChild(lighthouseHeader);
  
    for (const key in lighthouseMetrics) {
      const p = document.createElement('p');
      p.textContent = `${key}: ${lighthouseMetrics[key]}`;
      document.body.appendChild(p);
    }
  }
  
  run();