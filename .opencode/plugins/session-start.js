/* global process */
/**
 * Trellis Session Start Plugin
 *
 * Injects compact SessionStart context into the copy of the latest user
 * message that OpenCode sends to the model. Uses
 * `experimental.chat.messages.transform` so TUI / Web / SQLite history
 * stay untouched (issue #553).
 */

import { TrellisContext, debugLog, isTrellisSubagent } from "../lib/trellis-context.js"
import {
  MESSAGES_TRANSFORM_HOOK,
  platformInputFromMessages,
  prependEphemeralText,
  transcriptHasAssistantMessage,
} from "../lib/context-visibility.js"
import { buildSessionContext } from "../lib/session-utils.js"

const FIRST_REPLY_NOTICE_RE = /<first-reply-notice>[\s\S]*?<\/first-reply-notice>\s*/g

function stripFirstReplyNotice(context) {
  return context.replace(FIRST_REPLY_NOTICE_RE, "")
}

function applySessionStartTransform(ctx, messages, platformInput, systemParts = null) {
  try {
    const agent = platformInput?.agent || "unknown"
    debugLog("session", "applySessionStartTransform called, agent:", agent)

    if (isTrellisSubagent(platformInput)) {
      debugLog("session", "Skipping trellis subagent turn:", agent)
      return
    }

    if (process.env.TRELLIS_HOOKS === "0" || process.env.TRELLIS_DISABLE_HOOKS === "1") {
      debugLog("session", "Skipping - TRELLIS_HOOKS disabled")
      return
    }

    if (process.env.OPENCODE_NON_INTERACTIVE === "1") {
      debugLog("session", "Skipping - non-interactive mode")
      return
    }

    let context = buildSessionContext(ctx, platformInput)
    if (transcriptHasAssistantMessage(messages)) {
      context = stripFirstReplyNotice(context)
    }
    debugLog("session", "Built context, length:", context.length)
    const prepended = prependEphemeralText(messages, context)
    if (!prepended && Array.isArray(systemParts)) {
      systemParts.push({ type: "text", text: context })
    }
  } catch (error) {
    debugLog("session", "Error in session-start transform:", error.message, error.stack)
  }
}

// Dual export for OpenCode V2 ({ id, setup }) and V1 ({ id, server } or factory).
export default {
  id: "trellis-session-start",
  async setup(pluginCtx) {
    const directory = pluginCtx.location?.directory || process.cwd()
    const ctx = new TrellisContext(directory)
    debugLog("session", "Plugin loaded (V2), directory:", directory)

    if (pluginCtx.session?.hook) {
      await pluginCtx.session.hook("context", async (event) => {
        const platformInput = {
          sessionID: event.sessionID,
          agent: event.agent,
          ...platformInputFromMessages(event.messages),
        }
        applySessionStartTransform(ctx, event.messages, platformInput, event.system)
      })
    }
  },
  async server(input) {
    const directory = input?.directory || process.cwd()
    const ctx = new TrellisContext(directory)
    debugLog("session", "Plugin loaded (V1), directory:", directory)

    return {
      [MESSAGES_TRANSFORM_HOOK]: async (_input, output) => {
        const messages = output?.messages
        const platformInput = platformInputFromMessages(messages)
        applySessionStartTransform(ctx, messages, platformInput)
      },
    }
  },
}
