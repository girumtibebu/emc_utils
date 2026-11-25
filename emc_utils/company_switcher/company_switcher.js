// Company switcher for Desk: Frappe UI 1.0 native multi-company scoping dialog.
//
// Users with access to a single company don't get the row.
(function () {
	const METHOD = "emc_utils.company_scope.";
	let state = null;

	// SVG Icons matching Frappe UI 1.0 (Lucide icon set)
	const SVG_ICONS = {
		building: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<rect width="16" height="20" x="4" y="2" rx="2" ry="2"/>
			<path d="M9 22v-4h6v4"/>
			<path d="M8 6h.01"/>
			<path d="M16 6h.01"/>
			<path d="M12 6h.01"/>
			<path d="M12 10h.01"/>
			<path d="M12 14h.01"/>
			<path d="M16 10h.01"/>
			<path d="M16 14h.01"/>
			<path d="M8 10h.01"/>
			<path d="M8 14h.01"/>
		</svg>`,
		folder: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>
		</svg>`,
		search: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
			<circle cx="11" cy="11" r="8"/>
			<path d="m21 21-4.3-4.3"/>
		</svg>`,
		check: `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
			<polyline points="20 6 9 17 4 12"/>
		</svg>`,
		minus: `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
			<line x1="5" y1="12" x2="19" y2="12"/>
		</svg>`,
	};

	const leaves = () => (state?.companies || []).filter((c) => !c.is_group);
	const leaves_under = (name) => {
		const children = (state?.companies || []).filter((c) => c.parent === name);
		return children.flatMap((c) => (c.is_group ? leaves_under(c.name) : [c.name]));
	};

	function save_scope(companies, d) {
		if (!companies || !companies.length) {
			frappe.msgprint({
				title: __("Selection Required"),
				message: __("Please select at least one company."),
				indicator: "orange",
			});
			return;
		}

		if (d) {
			d.get_primary_btn().prop("disabled", true).text(__("Applying..."));
		}

		frappe.call({
			method: METHOD + "set_scope",
			args: { companies },
			freeze: true,
			freeze_message: __("Switching company scope..."),
			callback: function () {
				if (d) d.hide();
				window.location.reload();
			},
			error: function () {
				if (d) {
					d.get_primary_btn().prop("disabled", false).text(__("Apply"));
				}
			},
		});
	}

	function checkbox_html(id, extra_class, data_attrs) {
		return `
			<label class="emc-custom-checkbox" for="${id}">
				<input type="checkbox" id="${id}" class="emc-real-cb ${extra_class}" ${data_attrs}>
				<span class="emc-checkbox-box">
					<span class="emc-check-icon">${SVG_ICONS.check}</span>
					<span class="emc-minus-icon">${SVG_ICONS.minus}</span>
				</span>
			</label>
		`;
	}

	function show_company_dialog() {
		if (!state || !state.companies || !state.companies.length) return;

		const all_leaf_names = leaves().map((c) => c.name);
		const current_scope = new Set(state.scope || []);
		let temp_scope = new Set(current_scope);

		const d = new frappe.ui.Dialog({
			title: __("Select Companies"),
			size: "small",
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "switcher_html",
				},
			],
			primary_action_label: __("Apply"),
			primary_action: function () {
				save_scope([...temp_scope], d);
			},
			secondary_action_label: __("Cancel"),
			secondary_action: function () {
				d.hide();
			},
		});

		const $body = d.fields_dict.switcher_html.$wrapper;

		const groups = state.companies.filter((c) => c.is_group);
		const sorted_companies = [...state.companies].sort((a, b) => {
			if (a.is_group !== b.is_group) return a.is_group ? -1 : 1;
			return a.name.localeCompare(b.name);
		});

		let html = `
			<div class="emc-frappe-ui-modal">
				<p class="emc-modal-desc text-muted">
					${__("Select active companies for Desk transactions and views.")}
				</p>

				${
					sorted_companies.length > 3
						? `
				<div class="emc-search-wrapper">
					<span class="emc-search-icon">${SVG_ICONS.search}</span>
					<input type="text" class="form-control emc-search-input" placeholder="${__("Search companies...")}">
				</div>
				`
						: ""
				}

				<div class="emc-toolbar d-flex justify-content-between align-items-center mb-2 px-1">
					<label class="emc-select-all-wrap d-flex align-items-center mb-0" style="cursor:pointer;">
						${checkbox_html("emc-cb-all", "", "")}
						<span class="emc-select-all-label font-weight-500 ml-2" style="margin-left: 8px;">
							${__("Select All")}
						</span>
					</label>
					<span id="emc-selected-count" class="emc-counter-pill"></span>
				</div>

				<div class="emc-company-list">
		`;

		for (const comp of sorted_companies) {
			const is_group = comp.is_group;
			const is_child = comp.depth && comp.depth > 0;
			const escaped_name = frappe.utils.escape_html(comp.name);
			const cb_id = `emc-cb-${escaped_name}`;

			html += `
				<div class="emc-company-row ${is_group ? "emc-group-row" : "emc-leaf-row"} ${is_child ? "is-tree-child" : ""}" 
					 data-company="${escaped_name}">
					${checkbox_html(cb_id, is_group ? "emc-group-cb" : "emc-leaf-cb", `data-name="${escaped_name}"`)}
					<div class="emc-icon-badge" style="margin-left: 8px; margin-right: 10px;">
						${is_group ? SVG_ICONS.folder : SVG_ICONS.building}
					</div>
					<span class="emc-company-name ${is_group ? "font-weight-600" : ""}">
						${escaped_name}
					</span>
					${
						is_group
							? `<span class="emc-tag-group ml-auto" style="margin-left: auto;">Group</span>`
							: `<span class="emc-tag-abbr ml-auto" style="margin-left: auto;">${comp.abbr || ""}</span>`
					}
				</div>
			`;
		}

		html += `
					<div class="emc-empty-search text-muted text-center py-4" style="display:none; font-size:13px;">
						${__("No companies found.")}
					</div>
				</div>
			</div>
		`;

		$body.html(html);

		function refresh_ui() {
			let leaf_checked_count = 0;
			all_leaf_names.forEach((name) => {
				const is_on = temp_scope.has(name);
				if (is_on) leaf_checked_count++;
				const $cb = $body.find(`.emc-leaf-cb[data-name="${CSS.escape(name)}"]`);
				$cb.prop("checked", is_on);
				$cb.closest(".emc-company-row").toggleClass("is-checked", is_on);
			});

			groups.forEach((g) => {
				const under = leaves_under(g.name);
				const under_count = under.filter((n) => temp_scope.has(n)).length;
				const $gcb = $body.find(`.emc-group-cb[data-name="${CSS.escape(g.name)}"]`);
				const $grow = $gcb.closest(".emc-company-row");

				if (under_count === 0) {
					$gcb.prop("checked", false);
					$gcb.prop("indeterminate", false);
					$grow.removeClass("is-checked");
				} else if (under_count === under.length) {
					$gcb.prop("checked", true);
					$gcb.prop("indeterminate", false);
					$grow.addClass("is-checked");
				} else {
					$gcb.prop("checked", false);
					$gcb.prop("indeterminate", true);
					$grow.removeClass("is-checked");
				}
			});

			const $all_cb = $body.find("#emc-cb-all");
			if (leaf_checked_count === 0) {
				$all_cb.prop("checked", false);
				$all_cb.prop("indeterminate", false);
			} else if (leaf_checked_count === all_leaf_names.length) {
				$all_cb.prop("checked", true);
				$all_cb.prop("indeterminate", false);
			} else {
				$all_cb.prop("checked", false);
				$all_cb.prop("indeterminate", true);
			}

			$body.find("#emc-selected-count").text(
				leaf_checked_count === all_leaf_names.length
					? __("All ({0})", [leaf_checked_count])
					: __("{0} of {1} Selected", [leaf_checked_count, all_leaf_names.length])
			);
		}

		$body.on("click", ".emc-leaf-row", function (e) {
			if ($(e.target).is("input")) return;
			const $cb = $(this).find(".emc-leaf-cb");
			const name = $cb.attr("data-name");
			const new_state = !$cb.is(":checked");
			$cb.prop("checked", new_state);
			if (new_state) temp_scope.add(name);
			else temp_scope.delete(name);
			refresh_ui();
		});

		$body.on("change", ".emc-leaf-cb", function () {
			const name = $(this).attr("data-name");
			if ($(this).is(":checked")) temp_scope.add(name);
			else temp_scope.delete(name);
			refresh_ui();
		});

		$body.on("click", ".emc-group-row", function (e) {
			if ($(e.target).is("input")) return;
			const $cb = $(this).find(".emc-group-cb");
			const group_name = $cb.attr("data-name");
			const under = leaves_under(group_name);
			const all_on = under.every((n) => temp_scope.has(n));
			const set_to = !all_on;

			under.forEach((n) => {
				if (set_to) temp_scope.add(n);
				else temp_scope.delete(n);
			});
			refresh_ui();
		});

		$body.on("change", ".emc-group-cb", function () {
			const group_name = $(this).attr("data-name");
			const under = leaves_under(group_name);
			const set_to = $(this).is(":checked");

			under.forEach((n) => {
				if (set_to) temp_scope.add(n);
				else temp_scope.delete(n);
			});
			refresh_ui();
		});

		$body.on("change", "#emc-cb-all", function () {
			const is_checked = $(this).is(":checked");
			if (is_checked) {
				all_leaf_names.forEach((n) => temp_scope.add(n));
			} else {
				temp_scope.clear();
			}
			refresh_ui();
		});

		$body.on("input", ".emc-search-input", function () {
			const query = $(this).val().toLowerCase().trim();
			let matched = 0;
			$body.find(".emc-company-row").each(function () {
				const name = ($(this).attr("data-company") || "").toLowerCase();
				const is_match = !query || name.includes(query);
				$(this).toggle(is_match);
				if (is_match) matched++;
			});
			$body.find(".emc-empty-search").toggle(matched === 0);
		});

		refresh_ui();
		d.show();
	}

	// Install into Sidebar Header menu
	function install() {
		const Header = window.frappe?.ui?.SidebarHeader;
		if (!Header || Header.prototype.__company_switcher) return;
		const original = Header.prototype.menu_items;
		Header.prototype.menu_items = function () {
			const groups = original.call(this);
			if (!state || leaves().length < 2) return groups;

			const name_to_abbr = {};
			(state.companies || []).forEach((c) => {
				name_to_abbr[c.name] = c.abbr || c.name;
			});

			const active_companies = state.scope || [];
			const all_count = leaves().length;
			let summary = __("All");
			if (active_companies.length === all_count) {
				summary = __("All");
			} else if (active_companies.length === 1) {
				summary = name_to_abbr[active_companies[0]] || active_companies[0];
			} else if (active_companies.length > 1) {
				const abbrs = active_companies.map((n) => name_to_abbr[n] || n);
				const joined = abbrs.join(", ");
				summary = joined.length <= 14 ? joined : `${active_companies.length}`;
			}

			const row = {
				name: "company-switcher",
				label: `${__("Companies")} (${summary})`,
				icon: "building",
				onclick: () => show_company_dialog(),
			};

			const at = Math.min(1, groups.length);
			return [...groups.slice(0, at), { group: "", options: [row] }, ...groups.slice(at)];
		};
		Header.prototype.__company_switcher = true;
	}

	// Form print format per company
	const site_default_print_format = {};
	function apply_company_print_format(frm) {
		if (!frm?.meta || !frm.doc) return;
		const formats = frappe.boot.company_print_formats || {};
		if (!(frm.doctype in site_default_print_format)) {
			site_default_print_format[frm.doctype] = frm.meta.default_print_format || null;
		}
		const chosen = frm.doc.company && formats[frm.doc.company]?.[frm.doctype];
		frm.meta.default_print_format = chosen || site_default_print_format[frm.doctype];
	}

	$(document).on("form-refresh", (_e, frm) => apply_company_print_format(frm));

	// Expose globally for convenience
	window.frappe = window.frappe || {};
	window.frappe.show_company_switcher = show_company_dialog;

	$(document).on("app_ready startup", () => {
		if (frappe.session.user === "Guest") return;
		state = state || frappe.boot.company_switcher || null;
		install();
	});
})();
