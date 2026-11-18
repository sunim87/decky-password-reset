import { ButtonItem, ConfirmModal, PanelSection, PanelSectionRow, TextField, showModal, staticClasses } from "@decky/ui";
import { callable, definePlugin } from "@decky/api";
import { useEffect, useState } from "react";
import { FaKey } from "react-icons/fa";

type Status = { ready: boolean; user?: string; system?: string; message: string };
const statusCall = callable<[], Status>("get_status");
const resetCall = callable<[password: string, confirmation: string], { ok: boolean; message: string }>("reset_password");
function inputValue(event: unknown): string | undefined {
  if (typeof event === "string") return event;
  const value = (event as { target?: { value?: unknown } } | null)?.target?.value;
  return typeof value === "string" ? value : undefined;
}
function ResetDialog({ close }: { close: () => void }) {
  const [status, setStatus] = useState<Status>();
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  useEffect(() => {
    let active = true;
    statusCall().then(s => { if (active) setStatus(s); }).catch(() => { if (active) setMessage("플러그인 연결에 실패했습니다."); });
    return () => { active = false; };
  }, []);
  const reason = !status ? "계정 확인 중…" : !status.ready ? status.message : password.length < 4 ? "새 비밀번호를 4자 이상 입력하세요." : password.length > 128 ? "128자 이하로 입력하세요." : password !== confirmation ? "비밀번호 확인을 동일하게 입력하세요." : "재설정할 준비가 되었습니다.";
  const ready = !!status?.ready && password.length >= 4 && password.length <= 128 && password === confirmation;
  const apply = async () => {
    if (!ready || busy) return;
    setBusy(true); setMessage("");
    try { setMessage((await resetCall(password, confirmation)).message); }
    catch { setMessage("연결이 끊겼습니다. 비밀번호 상태를 확인하세요."); }
    finally { setPassword(""); setConfirmation(""); setBusy(false); }
  };
  return <ConfirmModal
    strTitle="비밀번호 재설정"
    strDescription={`${status?.system ?? ""} · ${status?.user ?? ""} · 로그인/sudo 함께 변경`}
    strOKButtonText={busy ? "변경 중…" : "재설정"}
    strCancelButtonText="닫기"
    bOKDisabled={!ready || busy}
    bCancelDisabled={busy}
    bDisableBackgroundDismiss
    closeModal={() => {}}
    onOK={apply}
    onCancel={() => { if (!busy) close(); }}>
    <div style={{ maxHeight: "45vh", overflowY: "auto" }}>
      <TextField label={`새 비밀번호 · ${password.length}자`} placeholder="4~128자" bIsPassword value={password} disabled={busy}
        onChange={e => { const next = inputValue(e); if (next !== undefined) setPassword(next); }} />
      <TextField label={`비밀번호 확인 · ${confirmation.length}자`} bIsPassword value={confirmation} disabled={busy}
        onChange={e => { const next = inputValue(e); if (next !== undefined) setConfirmation(next); }} />
      <div role="status" style={{ fontSize: 14, lineHeight: "20px", marginTop: 8 }}>{message || reason}</div>
    </div>
  </ConfirmModal>;
}
function openReset() {
  const modal = showModal(<ResetDialog close={() => modal.Close()} />);
}
function Content() {
  return <PanelSection title="관리자 비밀번호 재설정"><PanelSectionRow>
    <ButtonItem layout="below" onClick={openReset}>비밀번호 재설정 창 열기</ButtonItem>
  </PanelSectionRow></PanelSection>;
}
export default definePlugin(() => ({ name: "Password Reset", titleView: <div className={staticClasses.Title}>Password Reset</div>, content: <Content />, icon: <FaKey />, onDismount() {} }));
