function getSelectedJobId() {
  const params = new URLSearchParams(window.location.search)
  return params.get("job")
}

function getTabStorageKey() {
  const selectedJobId = getSelectedJobId()
  return selectedJobId ? `jobDetailTab:${selectedJobId}` : "jobDetailTab"
}

function getJobsPanelStorageKey() {
  const selectedJobId = getSelectedJobId()
  return selectedJobId ? `jobsPanelOpen:${selectedJobId}` : "jobsPanelOpen"
}

function updateIcons() {
  if (window.lucide) {
    lucide.createIcons()
  }
}

function setExpanded(button, expanded) {
  if (button) {
    button.setAttribute("aria-expanded", expanded ? "true" : "false")
  }
}

function showTab(id) {
  const tabs = ["desc", "answer", "interview", "cv"]
  const buttonMap = {
    desc: document.getElementById("tabDescBtn"),
    answer: document.getElementById("tabAnswerBtn"),
    interview: document.getElementById("tabInterviewBtn"),
    cv: document.getElementById("tabCvBtn")
  }

  let activeFound = false

  tabs.forEach(tabId => {
    const panel = document.getElementById(tabId)
    const button = buttonMap[tabId]
    const isActive = tabId === id

    if (panel) {
      panel.classList.toggle("hidden", !isActive)
      if (isActive) activeFound = true
    }

    if (button) {
      button.className = isActive
        ? "h-full whitespace-nowrap border-b-2 border-blue-600 text-sm font-medium text-blue-600 dark:border-blue-400 dark:text-blue-400"
        : "h-full whitespace-nowrap border-b-2 border-transparent text-sm text-zinc-500 transition hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
    }
  })

  const finalTab = activeFound ? id : "desc"
  sessionStorage.setItem(getTabStorageKey(), finalTab)

  const activeTabInput = document.getElementById("activeTabInput")
  if (activeTabInput) activeTabInput.value = finalTab
}

function updateCityDropdownLabel() {
  const checkboxes = Array.from(document.querySelectorAll('input[name="city"]'))
  const label = document.getElementById("cityDropdownLabel")
  if (!checkboxes.length || !label) return

  const checked = checkboxes.filter(cb => cb.checked)
  if (checked.length === 0 || checked.length === checkboxes.length) {
    label.textContent = "All cities"
  } else if (checked.length === 1) {
    label.textContent = checked[0].value
  } else {
    label.textContent = `${checked.length} cities selected`
  }
}

function setAllCities(checked) {
  document.querySelectorAll('input[name="city"]').forEach(cb => {
    cb.checked = checked
  })
  updateCityDropdownLabel()
}

function applyMobileJobsLayout(open) {
  const jobsAside = document.getElementById("jobsAside")
  const jobDetailSection = document.getElementById("jobDetailSection")
  const dashboardLayout = document.getElementById("dashboardLayout")
  const dashboardMain = document.getElementById("dashboardMain")
  const panel = document.getElementById("jobListScroll")
  const mobileNavPanel = document.getElementById("mobileNavPanel")
  const filterPanel = document.getElementById("filterPanel")
  const detailCard = document.getElementById("jobDetailCard")

  if (!jobsAside || !jobDetailSection || !dashboardLayout || !dashboardMain || !panel) return

  if (window.innerWidth >= 1024) {
    jobsAside.classList.remove("flex-1", "overflow-hidden")
    dashboardLayout.classList.remove("grid-rows-[minmax(0,1fr)]")
    dashboardMain.classList.add("overflow-hidden")
    jobDetailSection.classList.remove("hidden", "flex-1", "overflow-hidden")
    panel.classList.remove("h-auto")
    if (detailCard) detailCard.classList.add("h-full", "min-h-0", "flex-1")
    return
  }

  const navOpen = mobileNavPanel ? !mobileNavPanel.classList.contains("hidden") : false
  const filterOpen = filterPanel ? !filterPanel.classList.contains("hidden") : false

  if (open) {
    jobsAside.classList.add("flex-1", "overflow-hidden")
    dashboardLayout.classList.add("grid-rows-[minmax(0,1fr)]")
    dashboardMain.classList.add("overflow-hidden")
    jobDetailSection.classList.add("hidden")
    jobDetailSection.classList.remove("flex-1", "overflow-hidden")
    panel.classList.add("h-auto")
  } else {
    jobsAside.classList.remove("flex-1", "overflow-hidden")
    dashboardLayout.classList.remove("grid-rows-[minmax(0,1fr)]")
    dashboardMain.classList.add("overflow-hidden")
    jobDetailSection.classList.remove("hidden")
    jobDetailSection.classList.add("flex-1", "overflow-hidden")
    panel.classList.remove("h-auto")
  }

  if (detailCard) {
    if (!open && !navOpen && !filterOpen) {
      detailCard.classList.add("h-full", "min-h-0", "flex-1")
    } else {
      detailCard.classList.remove("h-full")
    }
  }
}

function setJobsPanelState(open) {
  const panel = document.getElementById("jobListScroll")
  const icon = document.getElementById("toggleJobsPanelIcon")
  const button = document.getElementById("toggleJobsPanelButton")
  if (!panel || !icon || !button) return

  if (window.innerWidth >= 1024) {
    panel.classList.remove("hidden")
    icon.setAttribute("data-lucide", "chevron-up")
    setExpanded(button, true)
    applyMobileJobsLayout(false)
    updateIcons()
    return
  }

  panel.classList.toggle("hidden", !open)
  icon.setAttribute("data-lucide", open ? "chevron-up" : "chevron-down")
  setExpanded(button, open)
  applyMobileJobsLayout(open)
  sessionStorage.setItem(getJobsPanelStorageKey(), open ? "open" : "closed")
  updateIcons()
}

function initializeJobsPanel() {
  if (window.innerWidth >= 1024) {
    setJobsPanelState(true)
    return
  }

  const savedState = sessionStorage.getItem(getJobsPanelStorageKey())
  if (savedState === "open") {
    setJobsPanelState(true)
  } else if (savedState === "closed") {
    setJobsPanelState(false)
  } else {
    setJobsPanelState(!getSelectedJobId())
  }
}

function toggleElement(button, panel, overlay) {
  const isHidden = panel.classList.contains("hidden")
  panel.classList.toggle("hidden", !isHidden)
  setExpanded(button, isHidden)

  if (overlay) {
    overlay.classList.toggle("hidden", !isHidden)
    overlay.classList.toggle("pointer-events-none", !isHidden)
  }
}

document.addEventListener("DOMContentLoaded", function () {
  updateIcons()

  const filterButton = document.getElementById("filterButton")
  const runSearchButtons = document.querySelectorAll(".run-search-trigger")
  const filterPanel = document.getElementById("filterPanel")
  const filterOverlay = document.getElementById("filterOverlay")
  const mobileNavButton = document.getElementById("mobileNavButton")
  const mobileNavPanel = document.getElementById("mobileNavPanel")
  const cityDropdownWrap = document.getElementById("cityDropdownWrap")
  const cityDropdownButton = document.getElementById("cityDropdownButton")
  const cityDropdownPanel = document.getElementById("cityDropdownPanel")
  const toggleJobsPanelButton = document.getElementById("toggleJobsPanelButton")
  const tabDescBtn = document.getElementById("tabDescBtn")
  const tabAnswerBtn = document.getElementById("tabAnswerBtn")
  const tabInterviewBtn = document.getElementById("tabInterviewBtn")
  const tabCvBtn = document.getElementById("tabCvBtn")
  const jobListScroll = document.getElementById("jobListScroll")
  const form = document.getElementById("jobUpdateForm")
  const filterDecisionInput = document.getElementById("filterDecisionInput")
  const filterDecisionButtons = document.querySelectorAll("[data-decision-value]")

  const savedTab = sessionStorage.getItem(getTabStorageKey()) || "desc"
  showTab(savedTab)
  updateCityDropdownLabel()
  initializeJobsPanel()

  document.querySelectorAll('input[name="city"]').forEach(cb => {
    cb.addEventListener("change", updateCityDropdownLabel)
  })

  const selectAllCitiesButton = document.getElementById("selectAllCitiesButton")
  const selectNoCitiesButton = document.getElementById("selectNoCitiesButton")
  if (selectAllCitiesButton) selectAllCitiesButton.addEventListener("click", () => setAllCities(true))
  if (selectNoCitiesButton) selectNoCitiesButton.addEventListener("click", () => setAllCities(false))

  if (cityDropdownButton && cityDropdownPanel) {
    cityDropdownButton.addEventListener("click", function (event) {
      event.stopPropagation()
      const isHidden = cityDropdownPanel.classList.contains("hidden")
      cityDropdownPanel.classList.toggle("hidden", !isHidden)
      setExpanded(cityDropdownButton, isHidden)
    })
  }

  if (filterButton && filterPanel && filterOverlay) {
    filterButton.addEventListener("click", function (event) {
      event.stopPropagation()

      if (mobileNavPanel && !mobileNavPanel.classList.contains("hidden")) {
        mobileNavPanel.classList.add("hidden")
        if (mobileNavButton) setExpanded(mobileNavButton, false)
      }

      if (window.innerWidth >= 768 && filterPanel.classList.contains("hidden")) {
        const rect = filterButton.getBoundingClientRect()
        const panelWidth = 420
        const gap = 8
        const margin = 12

        let left = rect.left
        if (left + panelWidth > window.innerWidth - margin) {
          left = window.innerWidth - panelWidth - margin
        }
        if (left < margin) {
          left = margin
        }

        filterPanel.style.left = `${Math.round(left)}px`
        filterPanel.style.top = `${Math.round(rect.bottom + gap)}px`
        filterPanel.style.right = "auto"
        filterPanel.style.bottom = "auto"
        filterPanel.style.width = `${panelWidth}px`
      }

      toggleElement(filterButton, filterPanel, filterOverlay)
      if (jobListScroll && window.innerWidth < 1024) {
        applyMobileJobsLayout(!jobListScroll.classList.contains("hidden"))
      }
    })
  }

  if (mobileNavButton && mobileNavPanel) {
    mobileNavButton.addEventListener("click", function (event) {
      event.stopPropagation()
      if (filterPanel && !filterPanel.classList.contains("hidden")) {
        filterPanel.classList.add("hidden")
        if (filterOverlay) filterOverlay.classList.add("hidden", "pointer-events-none")
        if (filterButton) setExpanded(filterButton, false)
      }
      const isHidden = mobileNavPanel.classList.contains("hidden")
      mobileNavPanel.classList.toggle("hidden", !isHidden)
      setExpanded(mobileNavButton, isHidden)
      if (jobListScroll && window.innerWidth < 1024) {
        applyMobileJobsLayout(!jobListScroll.classList.contains("hidden"))
      }
    })
  }

  if (toggleJobsPanelButton) {
    toggleJobsPanelButton.addEventListener("click", function () {
      if (!jobListScroll) return
      setJobsPanelState(jobListScroll.classList.contains("hidden"))
    })
  }

  if (tabDescBtn) tabDescBtn.addEventListener("click", () => showTab("desc"))
  if (tabAnswerBtn) tabAnswerBtn.addEventListener("click", () => showTab("answer"))
  if (tabInterviewBtn) tabInterviewBtn.addEventListener("click", () => showTab("interview"))
  if (tabCvBtn) tabCvBtn.addEventListener("click", () => showTab("cv"))

  if (jobListScroll) {
    const savedScrollTop = sessionStorage.getItem("jobListScrollTop")
    if (savedScrollTop !== null) {
      jobListScroll.scrollTop = parseInt(savedScrollTop, 10) || 0
    }

    jobListScroll.addEventListener("scroll", function () {
      sessionStorage.setItem("jobListScrollTop", String(jobListScroll.scrollTop))
    })

    document.querySelectorAll(".job-link").forEach(link => {
      link.addEventListener("click", function () {
        sessionStorage.setItem("jobListScrollTop", String(jobListScroll.scrollTop))
        if (window.innerWidth < 1024) {
          sessionStorage.setItem(getJobsPanelStorageKey(), "closed")
        }
      })
    })
  }

  if (filterDecisionButtons.length && filterDecisionInput) {
    filterDecisionButtons.forEach(button => {
      button.addEventListener("click", function () {
        const selectedValue = button.getAttribute("data-decision-value") || ""
        filterDecisionInput.value = selectedValue

        filterDecisionButtons.forEach(btn => {
          const value = btn.getAttribute("data-decision-value") || ""
          const active = value === selectedValue
          if (value === "") {
            btn.className = active
              ? "rounded-full px-3 py-2 text-sm transition bg-blue-600 text-white dark:bg-blue-500"
              : "rounded-full px-3 py-2 text-sm transition bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-500/10 dark:text-blue-300 dark:hover:bg-blue-500/15"
          } else if (value === "apply") {
            btn.className = active
              ? "rounded-full px-3 py-2 text-sm transition bg-green-600 text-white dark:bg-green-500"
              : "rounded-full px-3 py-2 text-sm transition bg-green-50 text-green-700 hover:bg-green-100 dark:bg-green-500/10 dark:text-green-300 dark:hover:bg-green-500/15"
          } else if (value === "pass") {
            btn.className = active
              ? "rounded-full px-3 py-2 text-sm transition bg-red-600 text-white dark:bg-red-500"
              : "rounded-full px-3 py-2 text-sm transition bg-red-50 text-red-700 hover:bg-red-100 dark:bg-red-500/10 dark:text-red-300 dark:hover:bg-red-500/15"
          } else if (value === "applied") {
            btn.className = active
              ? "rounded-full px-3 py-2 text-sm transition bg-sky-600 text-white dark:bg-sky-500"
              : "rounded-full px-3 py-2 text-sm transition bg-sky-50 text-sky-700 hover:bg-sky-100 dark:bg-sky-500/10 dark:text-sky-300 dark:hover:bg-sky-500/15"
          }
        })
      })
    })
  }

  if (form) {
    form.addEventListener("submit", function () {
      sessionStorage.setItem("jobListScrollTop", String(jobListScroll ? jobListScroll.scrollTop : 0))
      const activeTab = sessionStorage.getItem(getTabStorageKey()) || "desc"
      const activeTabInput = document.getElementById("activeTabInput")
      if (activeTabInput) activeTabInput.value = activeTab
    })
  }

  if (filterOverlay) {
    filterOverlay.addEventListener("click", function () {
      if (filterPanel) filterPanel.classList.add("hidden")
      filterOverlay.classList.add("hidden", "pointer-events-none")
      if (filterButton) setExpanded(filterButton, false)
      if (jobListScroll && window.innerWidth < 1024) {
        applyMobileJobsLayout(!jobListScroll.classList.contains("hidden"))
      }
    })
  }

  document.addEventListener("click", function (event) {
    if (cityDropdownWrap && cityDropdownPanel && !cityDropdownWrap.contains(event.target)) {
      cityDropdownPanel.classList.add("hidden")
      setExpanded(cityDropdownButton, false)
    }

    if (filterPanel && filterButton && !filterPanel.classList.contains("hidden") && !filterPanel.contains(event.target) && !filterButton.contains(event.target)) {
      filterPanel.classList.add("hidden")
      if (filterOverlay) filterOverlay.classList.add("hidden", "pointer-events-none")
      setExpanded(filterButton, false)
      if (jobListScroll && window.innerWidth < 1024) {
        applyMobileJobsLayout(!jobListScroll.classList.contains("hidden"))
      }
    }

    if (mobileNavPanel && mobileNavButton && !mobileNavPanel.classList.contains("hidden") && !mobileNavPanel.contains(event.target) && !mobileNavButton.contains(event.target)) {
      mobileNavPanel.classList.add("hidden")
      setExpanded(mobileNavButton, false)
      if (jobListScroll && window.innerWidth < 1024) {
        applyMobileJobsLayout(!jobListScroll.classList.contains("hidden"))
      }
    }
  })

  runSearchButtons.forEach(button => {
    button.addEventListener("click", function () {
      window.dispatchEvent(new CustomEvent("jobtrackr:run-search"))
    })
  })

  window.addEventListener("resize", function () {
    initializeJobsPanel()
    if (window.innerWidth >= 1024) {
      if (mobileNavPanel) mobileNavPanel.classList.add("hidden")
      if (mobileNavButton) setExpanded(mobileNavButton, false)
      if (filterOverlay) filterOverlay.classList.add("hidden", "pointer-events-none")
    }

    if (window.innerWidth >= 768 && filterPanel && filterButton && !filterPanel.classList.contains("hidden")) {
      const rect = filterButton.getBoundingClientRect()
      const panelWidth = 420
      const gap = 8
      const margin = 12

      let left = rect.left
      if (left + panelWidth > window.innerWidth - margin) {
        left = window.innerWidth - panelWidth - margin
      }
      if (left < margin) {
        left = margin
      }

      filterPanel.style.left = `${Math.round(left)}px`
      filterPanel.style.top = `${Math.round(rect.bottom + gap)}px`
      filterPanel.style.right = "auto"
      filterPanel.style.bottom = "auto"
      filterPanel.style.width = `${panelWidth}px`
    }
  })
})