import React, { useState } from "react";
import {
  BookOpen,
  Users,
  Calendar,
  Search,
  ChevronDown,
  ChevronRight,
  UserCheck,
} from "lucide-react";

export default function OptionGroupViewer({ optionBlocks = [] }) {
  const [searchFilter, setSearchFilter] = useState("");
  const [expandedBlocks, setExpandedBlocks] = useState({});

  const toggleBlock = (key) => {
    setExpandedBlocks((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  if (!optionBlocks.length) {
    return (
      <div className="p-8 text-center border border-slate-800 rounded-xl bg-slate-900/20 text-xs text-slate-400">
        No elective option blocks or parallel groups detected in this staging
        batch.
      </div>
    );
  }

  // Filter blocks by group identifier or subject code
  const filteredBlocks = optionBlocks.filter((block) => {
    const term = searchFilter.toLowerCase();
    const identifier = (
      block.group_identifier ||
      block.ClassCode ||
      ""
    ).toLowerCase();
    const subject = (
      block.subject_code ||
      block.SubjectCode ||
      ""
    ).toLowerCase();
    const cohort = (
      block.academic_cohort ||
      block.YearGroup ||
      ""
    ).toLowerCase();
    return (
      identifier.includes(term) ||
      subject.includes(term) ||
      cohort.includes(term)
    );
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Option Blocks & Elective Enrollments
          </h3>
          <p className="text-xs text-slate-400">
            Parallel timetable groupings and student roster allocations (
            {filteredBlocks.length} groups)
          </p>
        </div>

        <div className="relative">
          <input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Filter by group, cohort, or subject..."
            className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 outline-none w-64 focus:border-emerald-500"
          />
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredBlocks.map((block, idx) => {
          const blockKey = `${block.group_identifier || block.ClassCode || idx}`;
          const isExpanded = !!expandedBlocks[blockKey];
          const students = block.students || block.EnrolledStudents || [];
          const studentCount =
            block.student_count || block.StudentCount || students.length;

          return (
            <div
              key={blockKey}
              className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden transition-colors"
            >
              <div
                onClick={() => toggleBlock(blockKey)}
                className="p-4 cursor-pointer hover:bg-slate-800/30 flex items-start justify-between gap-3"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-semibold text-slate-100">
                      {block.group_identifier || block.ClassCode}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {block.subject_code || block.SubjectCode}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-[11px] text-slate-400">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      Cohort:{" "}
                      {block.academic_cohort ||
                        block.YearGroup ||
                        "Year Cohort"}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3 text-slate-500" />
                      {studentCount} Enrolled
                    </span>
                  </div>
                </div>

                <button className="text-slate-400 hover:text-slate-200 p-1">
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </button>
              </div>

              {isExpanded && (
                <div className="border-t border-slate-800/80 bg-slate-950/60 p-3 space-y-2">
                  <p className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 flex items-center gap-1">
                    <UserCheck className="w-3 h-3 text-emerald-400" /> Enrolled
                    Pupils
                  </p>

                  {!students.length ? (
                    <p className="text-[11px] text-slate-500 italic">
                      No specific pupils mapped in this option payload.
                    </p>
                  ) : (
                    <div className="max-h-48 overflow-y-auto space-y-1 pr-1 font-mono text-[11px]">
                      {students.map((student, sIdx) => (
                        <div
                          key={sIdx}
                          className="flex items-center justify-between p-1.5 bg-slate-900/80 rounded border border-slate-800/60"
                        >
                          <div className="flex items-center gap-2 truncate">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                            <span className="text-slate-200 truncate">
                              {student.student_name}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            {student.base_class && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-sans">
                                {student.base_class}
                              </span>
                            )}
                            <span className="text-slate-500 text-[10px]">
                              {student.idnumber || student.untis_student_id}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
