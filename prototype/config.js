/**
 * 智聘星图 - Elite Talent System 共享设计配置
 * 基于 Electric Emerald + Glassmorphism 设计体系
 */
(function() {
    tailwind.config = {
        darkMode: "class",
        theme: {
            extend: {
                colors: {
                    "primary": "#003527",
                    "on-primary": "#ffffff",
                    "primary-container": "#2b6954",
                    "on-primary-container": "#efefff",
                    "inverse-primary": "#95d3ba",
                    "surface": "#f8f9fa",
                    "surface-dim": "#d9dadb",
                    "surface-bright": "#f8f9fa",
                    "surface-container-lowest": "#ffffff",
                    "surface-container-low": "#f3f4f5",
                    "surface-container": "#edeeef",
                    "surface-container-high": "#e7e8e9",
                    "surface-container-highest": "#e1e3e4",
                    "on-surface": "#191c1d",
                    "on-surface-variant": "#434656",
                    "inverse-surface": "#2e3132",
                    "inverse-on-surface": "#f0f1f2",
                    "outline": "#747688",
                    "outline-variant": "#c4c5d9",
                    "secondary": "#5f5e5e",
                    "on-secondary": "#ffffff",
                    "secondary-container": "#e5e2e1",
                    "on-secondary-container": "#656464",
                    "tertiary": "#993100",
                    "on-tertiary": "#ffffff",
                    "tertiary-container": "#c24100",
                    "on-tertiary-container": "#ffece6",
                    "error": "#ba1a1a",
                    "on-error": "#ffffff",
                    "error-container": "#ffdad6",
                    "on-error-container": "#93000a",
                    "primary-fixed": "#b0f0d6",
                    "primary-fixed-dim": "#95d3ba",
                    "on-primary-fixed": "#002117",
                    "on-primary-fixed-variant": "#00251a",
                    "secondary-fixed": "#e5e2e1",
                    "secondary-fixed-dim": "#c8c6c5",
                    "on-secondary-fixed": "#1c1b1b",
                    "on-secondary-fixed-variant": "#474646",
                    "tertiary-fixed": "#ffdbcf",
                    "tertiary-fixed-dim": "#ffb59b",
                    "on-tertiary-fixed": "#380d00",
                    "on-tertiary-fixed-variant": "#812800",
                    "background": "#f8f9fa",
                    "on-background": "#191c1d",
                    "surface-variant": "#e1e3e4",
                    "surface-tint": "#124af0"
                },
                borderRadius: {
                    "DEFAULT": "0.25rem",
                    "sm": "0.125rem",
                    "md": "0.375rem",
                    "lg": "0.5rem",
                    "xl": "0.75rem",
                    "2xl": "1rem",
                    "3xl": "1.5rem",
                    "full": "9999px"
                },
                spacing: {
                    "base": "8px",
                    "xs": "4px",
                    "sm": "12px",
                    "md": "24px",
                    "lg": "48px",
                    "xl": "80px",
                    "container-max": "1440px",
                    "gutter": "24px",
                    "margin-mobile": "16px",
                    "margin-desktop": "64px"
                },
                fontFamily: {
                    "display-lg": ["Inter"],
                    "body-md": ["Inter"],
                    "headline-lg": ["Inter"],
                    "headline-md": ["Inter"],
                    "body-lg": ["Inter"],
                    "label-caps": ["Inter"],
                    "button": ["Inter"]
                },
                fontSize: {
                    "display-lg": ["64px", { lineHeight: "72px", letterSpacing: "-0.04em", fontWeight: "700" }],
                    "display-lg-mobile": ["40px", { lineHeight: "48px", letterSpacing: "-0.03em", fontWeight: "700" }],
                    "headline-lg": ["32px", { lineHeight: "40px", letterSpacing: "-0.02em", fontWeight: "600" }],
                    "headline-md": ["24px", { lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600" }],
                    "body-lg": ["18px", { lineHeight: "28px", fontWeight: "400" }],
                    "body-md": ["16px", { lineHeight: "24px", fontWeight: "400" }],
                    "label-caps": ["12px", { lineHeight: "16px", letterSpacing: "0.1em", fontWeight: "700" }],
                    "button": ["14px", { lineHeight: "20px", letterSpacing: "0.02em", fontWeight: "600" }]
                }
            }
        }
    };
})();
