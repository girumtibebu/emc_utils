// Company switcher for Desk: Multi-company scoping with proper checkboxes and Apply button.
//
// Users with access to a single company don't get the row.
(function () {
	const METHOD = "emc_utils.company_scope.";
	let state = null;

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
			callback: function (r) {
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

	function show_company_dialog() {
		if (!state || !state.companies || !state.companies.length) return;

		const all_leaf_names = leaves().map((c) => c.name);
		const current_scope = new Set(state.scope || []);
		// working copy of selected leaf companies
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

		// Build UI
		const groups = state.companies.filter((c) => c.is_group);
		const sorted_companies = [...state.companies].sort((a, b) => {
			if (a.is_group !== b.is_group) return a.is_group ? -1 : 1;
			return a.name.localeCompare(b.name);
		});

		let html = `
			<div class="emc-switcher-modal">
				<p class="text-muted small mb-3">
					${__("Select the companies you want to view across Desk. Click Apply to update.")}
				</p>
				<div class="emc-switcher-header d-flex justify-content-between align-items-center pb-2 mb-2 border-bottom">
					<label class="emc-cb-label font-weight-bold d-flex align-items-center mb-0" style="cursor:pointer;">
						<input type="checkbox" id="emc-cb-all" class="emc-checkbox mr-2">
						<span>${__("Select All")}</span>
					</label>
					<span id="emc-selected-count" class="badge badge-secondary" style="font-size:12px; font-weight:normal; padding: 4px 8px;"></span>
				</div>
				<div class="emc-company-list" style="max-height: 320px; overflow-y: auto; padding-right: 2px;">
		`;

		// Group-first or Tree view
		// Let's render hierarchical if parents exist, otherwise flat list
		for (const comp of sorted_companies) {
			const is_group = comp.is_group;
			const indent = comp.depth && comp.depth > 0 ? "margin-left: 20px;" : "";
			const icon = is_group ? "folder" : "building";
			const tag = is_group
				? `<span class="badge badge-light text-muted ml-auto" style="font-size:11px;">Group</span>`
				: `<span class="badge badge-light text-muted ml-auto" style="font-size:11px;">${comp.abbr || ""}</span>`;

			html += `
				<div class="emc-company-item d-flex align-items-center py-2 px-2 rounded mb-1 ${is_group ? "emc-is-group" : "emc-is-leaf"}" 
					 data-company="${comp.name}" data-is-group="${is_group ? "1" : "0"}" style="${indent} cursor:pointer; user-select:none;">
					<input type="checkbox" class="emc-checkbox mr-2 ${is_group ? "emc-group-cb" : "emc-leaf-cb"}" 
						   id="emc-cb-${frappe.utils.escape_html(comp.name)}" 
						   data-name="${frappe.utils.escape_html(comp.name)}" 
						   style="cursor:pointer; width:16px; height:16px; margin: 0 8px 0 0;">
					<span class="emc-icon mr-2 text-muted" style="margin-right:6px;">
						${is_group ? "📁" : "🏢"}
					</span>
					<span class="emc-name ${is_group ? "font-weight-bold" : ""}">
						${frappe.utils.escape_html(comp.name)}
					</span>
					${tag}
				</div>
			`;
		}

		html += `
				</div>
			</div>
		`;

		$body.html(html);

		// Helper to refresh checkbox states and counts
		function refresh_ui() {
			let leaf_checked_count = 0;
			all_leaf_names.forEach((name) => {
				const is_on = temp_scope.has(name);
				if (is_on) leaf_checked_count++;
				const $cb = $body.find(`.emc-leaf-cb[data-name="${CSS.escape(name)}"]`);
				$cb.prop("checked", is_on);
				$cb.closest(".emc-company-item").toggleClass("emc-item-active", is_on);
			});

			// Update Group checkboxes
			groups.forEach((g) => {
				const under = leaves_under(g.name);
				const under_count = under.filter((n) => temp_scope.has(n)).length;
				const $gcb = $body.find(`.emc-group-cb[data-name="${CSS.escape(g.name)}"]`);
				if (under_count === 0) {
					$gcb.prop("checked", false);
					$gcb.prop("indeterminate", false);
					$gcb.closest(".emc-company-item").removeClass("emc-item-active");
				} else if (under_count === under.length) {
					$gcb.prop("checked", true);
					$gcb.prop("indeterminate", false);
					$gcb.closest(".emc-company-item").addClass("emc-item-active");
				} else {
					$gcb.prop("checked", false);
					$gcb.prop("indeterminate", true);
					$gcb.closest(".emc-company-item").removeClass("emc-item-active");
				}
			});

			// Update Select All checkbox
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

			// Update counter
			$body.find("#emc-selected-count").text(
				leaf_checked_count === all_leaf_names.length
					? __("All ({0}) Selected", [leaf_checked_count])
					: __("{0} of {1} Selected", [leaf_checked_count, all_leaf_names.length])
			);
		}

		// Leaf checkbox / row click
		$body.on("click", ".emc-is-leaf", function (e) {
			const $target = $(e.target);
			const $cb = $(this).find(".emc-leaf-cb");
			const name = $cb.attr("data-name");

			let new_state;
			if ($target.is(".emc-leaf-cb")) {
				new_state = $target.is(":checked");
			} else {
				new_state = !$cb.is(":checked");
				$cb.prop("checked", new_state);
			}

			if (new_state) {
				temp_scope.add(name);
			} else {
				temp_scope.delete(name);
			}
			refresh_ui();
		});

		// Group checkbox / row click
		$body.on("click", ".emc-is-group", function (e) {
			const $target = $(e.target);
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

		// Select All click
		$body.on("change", "#emc-cb-all", function () {
			const is_checked = $(this).is(":checked");
			if (is_checked) {
				all_leaf_names.forEach((n) => temp_scope.add(n));
			} else {
				temp_scope.clear();
			}
			refresh_ui();
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

			const active_count = (state.scope || []).length;
			const all_count = leaves().length;
			let summary = __("All");
			if (active_count === 1) {
				summary = state.scope[0];
			} else if (active_count < all_count) {
				summary = `${active_count} ${__("Selected")}`;
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
